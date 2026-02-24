# CYO Backend

基于混沌算法的图像目标检测与加密解密系统后端。

## 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.10.x |
| uv | >= 0.1 |
| Visual Studio Build Tools | 2022（含 C++ 桌面开发工作负载） |

## 项目初始化

### 1. 安装 uv

如果尚未安装 [uv](https://docs.astral.sh/uv/)：

```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 创建虚拟环境并安装依赖

```bash
# 在项目根目录下
cd backend
uv sync
```

`uv sync` 会自动：
- 根据 `pyproject.toml` 中的 `requires-python = "==3.10.*"` 找到或下载对应的 Python
- 创建 `.venv` 虚拟环境
- 安装所有 `dependencies` 和 `dev` 依赖组

### 3. 构建 C++ 加密模块

加密/解密核心算法使用 C++ 实现（通过 pybind11 绑定），需要编译后才能使用：

```bash
# 方式一：使用构建脚本（推荐）
build_cpp.bat

# 方式二：手动构建
uv run python setup.py build_ext --inplace
```

**前置条件：**
- 安装 [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- 选择 **"使用 C++ 的桌面开发"** 工作负载

构建成功后，模块 `cyo.chaos_crypto_cpp` 会被编译到 `cyo/` 目录下（文件名类似 `chaos_crypto_cpp.cp310-win_amd64.pyd`）。

> **注意：** 如果 C++ 模块未构建，系统会自动回退到纯 Python 实现，功能不受影响，但运行速度较慢。

### 4. 验证安装

```bash
# 验证 C++ 模块
uv run python -c "from cyo.chaos_crypto_cpp import encryption, decryption; print('C++ module OK')"

# 运行测试
uv run pytest test/ -v
```

### 5. 启动服务

```bash
uv run python main.py
```

## 项目结构

```
backend/
├── main.py                  # 应用入口
├── pyproject.toml           # 项目配置 & 依赖声明（uv）
├── setup.py                 # C++ 扩展构建配置
├── build_cpp.bat            # C++ 一键构建脚本
├── models/                  # ONNX 模型文件
│   ├── CCPD.onnx
│   ├── CelebA.onnx
│   └── HRSC2016.onnx
├── cyo/
│   ├── __init__.py
│   ├── constants.py
│   ├── main.py              # FastAPI 应用定义
│   ├── api/
│   │   ├── chaos_analysis.py    # 混沌分析 API
│   │   ├── image_analysis.py    # 图像分析 API
│   │   └── image_processing.py  # 加密/解密/检测 API
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── chaos_algorithm.py   # 加密/解密入口（自动选 C++ 或 Python）
│   │   ├── detect.py
│   │   └── yolo_engine.py       # YOLO 推理引擎
│   ├── utils/
│   │   ├── chaos.py             # 混沌序列生成 & 分析（Python）
│   │   ├── draw_frame.py
│   │   ├── file_process.py
│   │   └── general.py
│   └── cpp_ext/                 # C++ 加密模块源码
│       ├── CMakeLists.txt       # CMake 构建配置（可选）
│       ├── utils.h              # 通用工具函数
│       ├── chaos_sequence.h/cpp # 混沌序列生成
│       ├── encryption.h/cpp     # 加密算法
│       ├── decryption.h/cpp     # 解密算法
│       └── bindings.cpp         # pybind11 模块定义
├── static/                  # 静态资源目录
└── test/                    # 测试
    ├── test_chaos.py
    ├── test_cpp_crypto.py       # C++ vs Python 对比测试
    ├── test_draw_frame.py
    ├── test_image_process_flow.py
    └── test_yolo_engine.py
```

## C++ 加密模块

### 架构

C++ 代码位于 `cyo/cpp_ext/`，拆分为以下模块：

| 文件 | 职责 |
|------|------|
| `utils.h` | 通用内联工具函数（GCD、Python 风格取模、Fortran 序 flatten/reshape、数组循环移位） |
| `chaos_sequence.h/cpp` | 混沌序列生成（`generate_p_q`）、R 矩阵计算（`get_R_matrices`）、密钥解析（`parse_key`） |
| `encryption.h/cpp` | 图像加密：十字交叉置换 → 逆向扩散 → 正向扩散 |
| `decryption.h/cpp` | 图像解密：逆正向扩散 → 逆逆向扩散 → 逆十字交叉置换 |
| `bindings.cpp` | pybind11 模块注册，导出 `encryption()` 和 `decryption()` 函数 |

所有 C++ 代码在 `chaos` 命名空间下。

### 自动回退机制

`cyo/services/chaos_algorithm.py` 在导入时自动检测 C++ 模块是否可用：

```python
from cyo.services.chaos_algorithm import encryption, decryption
# 自动使用 C++ 实现（如果已编译），否则回退到 Python
```

项目中所有调用 `encryption` / `decryption` 的代码无需任何修改。

### 重新构建

修改 C++ 代码后需要重新编译：

```bash
uv run python setup.py build_ext --inplace
```

## 运行测试

```bash
# 运行所有测试
uv run pytest test/ -v

# 仅运行 C++ 对比测试
uv run pytest test/test_cpp_crypto.py -v

# 运行加密端到端测试
uv run pytest test/test_image_process_flow.py -v
```
