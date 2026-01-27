import numpy as np
from numpy import sin as sin
from numpy import pi as pi

def get_p_and_q(Sum: int, p1: float, q1: float):
    p = np.zeros(Sum*3 + 1000)
    q = np.zeros(Sum*3 + 1000)
    a = 0.6
    k = 0.8
    p[0] = p1
    q[0] = q1
    for i in range(Sum*3 + 999):
        p[i + 1] = sin( 21 / (a*k*p[i] * (q[i] + 3) * (1 - k*p[i])))
        q[i + 1] = sin( 21 / (a*q[i] * (k*p[i + 1] + 3) * (1 - q[i])))
    
    # print(p)
    p = p[1000:Sum*3 + 1000]
    p = np.divide(np.add(p, a), 2 * a)
    p = np.divide(np.floor(p * np.pow(10, 4)), np.pow(10, 4))

    q = q[1000:Sum*3 + 1000]
    q = np.divide(q, k)
    q = np.divide(np.floor(q*np.pow(10, 4)), np.pow(10, 4)) 
    q = np.abs(q)
    return p, q

def get_R_matrix(W: int, M: int, p1: float, q1: float):
    Sum = W * M
    p, q = get_p_and_q(Sum, p1, q1)

    q1 = q[:Sum]
    q2 = q[Sum: 2*Sum]
    q3 = q[2*Sum: len(p)]

    RR = np.reshape(q1, (W, M), order='F').T
    RG = np.reshape(q2, (W, M), order='F').T
    RB = np.reshape(q3, (W, M), order='F').T

    return RR, RG, RB, p, q

import numpy as np
import math
from numba import jit

@jit(nopython=True)
def iter_system(x, y, a, k):
    """
    单步迭代：计算 x(n+1), y(n+1)
    """
    denom_x = a * (y + 3) * k * x * (1 - k * x)
    if abs(denom_x) < 1e-10: denom_x = 1e-10
    x_next = math.sin(21 / denom_x)
    
    denom_y = a * (k * x_next + 3) * y * (1 - y)
    if abs(denom_y) < 1e-10: denom_y = 1e-10
    y_next = math.sin(21 / denom_y)
    
    return x_next, y_next


@jit(nopython=True)
def calc_jacobian(x, y, x_next, a, k):
    """
    计算雅可比矩阵的四个元素 J = [[Xx, Xy], [Yx, Yy]]
    这是之前重复度最高的代码段，现在封装起来
    """
    # 重新计算中间变量 (为了求导)
    # 注意：这里需要 careful，求导时用的 x 是 x(n)，不是 x(n+1)
    
    # Base 1 (针对 x 方程)
    denom_x = a * (y + 3) * k * x * (1 - k * x)
    if abs(denom_x) < 1e-10: denom_x = 1e-10
    base1 = 21 / denom_x
    
    # Base 2 (针对 y 方程，注意 y方程里用的是 x_next)
    denom_y = a * (k * x_next + 3) * y * (1 - y)
    if abs(denom_y) < 1e-10: denom_y = 1e-10
    base2 = 21 / denom_y

    # 偏导数公式
    Xx = -math.cos(base1) * base1 * (1 - 2 * k * x) / (x * (1 - k * x) + 1e-12)
    Xy = -math.cos(base1) * base1 / (y + 3)
    
    Yx = -math.cos(base2) * base2 * k * Xx / (k * x_next + 3)
    Yy = -math.cos(base2) * base2 * (1 - 2 * y) / (y * (1 - y) + 1e-12)
    
    return Xx, Xy, Yx, Yy

def calculate_phase_diagram(a, k, iterations=10000, keep_last=2000):
    """
    计算特定 K 值下的相图 (Phase Portrait)
    通常需要保存比分岔图更多的点来画出清晰的轨迹
    """
    x_traj = []
    y_traj = []
    
    x, y = 0.01, 0.01
    
    for n in range(iterations):
        x, y = iter_system(x, y, a, k)
        
        if n >= iterations - keep_last:
            x_traj.append(x)
            y_traj.append(y)
            
    return x_traj, y_traj

@jit(nopython=True)
def compute_for_varying_k(a_fixed, k_start, k_end, step, iterations=5000, keep_last=100, transient=300):
    """
    专门处理 K 变化的情况
    返回:
      - k_axis: K 轴坐标
      - bif_x, bif_y: 分岔图数据 (展平)
      - le1, le2: Lyapunov 指数
    """
    # 1. 生成 K 序列
    # numba 不支持 np.arange 的 step 为 float (有时会有问题)，建议手动生成
    num_steps = int((k_end - k_start) / step) + 1
    k_values = np.linspace(k_start, k_end, num_steps)
    
    # 结果容器
    bif_x = []
    bif_y = [] # 暂时存成一维，后面重组
    le1_arr = np.zeros(num_steps)
    le2_arr = np.zeros(num_steps)
    
    x_init, y_init = 0.01, 0.01
    
    for i in range(num_steps):
        k = k_values[i]
        a = a_fixed  # A 是固定的
        
        x, y = x_init, y_init
        Q = np.eye(2)
        sum_log_r1 = 0.0
        sum_log_r2 = 0.0
        
        # 迭代循环
        for n in range(iterations):
            x_prev, y_prev = x, y
            x, y = iter_system(x, y, a, k)
            
            # --- 分岔图数据收集 ---
            if n >= iterations - keep_last:
                bif_x.append(k) # X轴是 K
                bif_y.append(x) # Y轴是 x(n)
                
            # --- Lyapunov 计算 ---
            # 调用封装好的雅可比计算
            Xx, Xy, Yx, Yy = calc_jacobian(x_prev, y_prev, x, a, k)
            
            J = np.array([[Xx, Xy], [Yx, Yy]])
            B = np.dot(J, Q)
            Q, R = np.linalg.qr(B)
            
            if n >= transient:
                sum_log_r1 += math.log(abs(R[0, 0]) + 1e-12)
                sum_log_r2 += math.log(abs(R[1, 1]) + 1e-12)

        # 记录当前 K 的 LE 平均值
        valid_steps = iterations - transient
        le1_arr[i] = sum_log_r1 / valid_steps
        le2_arr[i] = sum_log_r2 / valid_steps
            
    return k_values, bif_x, bif_y, le1_arr, le2_arr


@jit(nopython=True)
def compute_for_varying_a(k_fixed, a_start, a_end, step, iterations=5000, keep_last=100, transient=300):
    """
    专门处理 A 变化的情况
    结构与上面类似，但迭代变量变成了 A
    """
    num_steps = int((a_end - a_start) / step) + 1
    a_values = np.linspace(a_start, a_end, num_steps)
    
    bif_x = []
    bif_y = []
    le1_arr = np.zeros(num_steps)
    le2_arr = np.zeros(num_steps)
    
    x_init, y_init = 0.01, 0.01
    
    for i in range(num_steps):
        a = a_values[i]
        k = k_fixed # K 是固定的
        
        x, y = x_init, y_init
        Q = np.eye(2)
        sum_log_r1 = 0.0
        sum_log_r2 = 0.0
        
        for n in range(iterations):
            x_prev, y_prev = x, y
            x, y = iter_system(x, y, a, k)
            
            # --- 分岔图数据收集 ---
            if n >= iterations - keep_last:
                bif_x.append(a) # X轴是 A
                bif_y.append(x) # Y轴是 x(n)
                
            # --- Lyapunov 计算 ---
            Xx, Xy, Yx, Yy = calc_jacobian(x_prev, y_prev, x, a, k)
            
            J = np.array([[Xx, Xy], [Yx, Yy]])
            B = np.dot(J, Q)
            Q, R = np.linalg.qr(B)
            
            if n >= transient:
                sum_log_r1 += math.log(abs(R[0, 0]) + 1e-12)
                sum_log_r2 += math.log(abs(R[1, 1]) + 1e-12)

        valid_steps = iterations - transient
        le1_arr[i] = sum_log_r1 / valid_steps
        le2_arr[i] = sum_log_r2 / valid_steps
            
    return a_values, bif_x, bif_y, le1_arr, le2_arr

    """
    计算 Lyapunov 指数谱 (LE1, LE2)
    """
    le1_data = [] # 格式 [[k, le1], ...]
    le2_data = [] # 格式 [[k, le2], ...]
    
    x_init, y_init = 0.01, 0.01

    for k in k_values:
        x, y = x_init, y_init
        Q = np.eye(2)
        sum_log_r1 = 0.0
        sum_log_r2 = 0.0
        
        for n in range(iterations):
            # 1. 先计算系统的下一个状态，因为雅可比矩阵可能需要 x_next
            x_prev, y_prev = x, y # 保存旧值用于导数计算
            x, y = _iter_system(x, y, a, k) # x, y 变为 n+1 时刻
            
            # 2. 计算雅可比矩阵 (Jacobian)
            # 重新计算分母项以便求导 (使用 prev 值)
            denom_x = a * (y_prev + 3) * k * x_prev * (1 - k * x_prev)
            if abs(denom_x) < 1e-10: denom_x = 1e-10
            base1 = 21 / denom_x
            
            denom_y = a * (k * x + 3) * y_prev * (1 - y_prev) # 注意这里中间项用的是 x (即 x_next)
            if abs(denom_y) < 1e-10: denom_y = 1e-10
            base2 = 21 / denom_y

            # 导数项
            # Xx = d(f)/dx
            Xx = -math.cos(base1) * base1 * (1 - 2 * k * x_prev) / (x_prev * (1 - k * x_prev) + 1e-12)
            # Xy = d(f)/dy
            Xy = -math.cos(base1) * base1 / (y_prev + 3)
            # Yx = d(g)/dx
            Yx = -math.cos(base2) * base2 * k * Xx / (k * x + 3)
            # Yy = d(g)/dy
            Yy = -math.cos(base2) * base2 * (1 - 2 * y_prev) / (y_prev * (1 - y_prev) + 1e-12)
            
            # 3. QR 分解与 LE 累加
            J = np.array([[Xx, Xy], [Yx, Yy]])
            B = np.dot(J, Q)
            Q, R = np.linalg.qr(B)
            
            if n >= transient:
                sum_log_r1 += math.log(abs(R[0, 0]) + 1e-12)
                sum_log_r2 += math.log(abs(R[1, 1]) + 1e-12)

        # 计算平均值
        valid_steps = iterations - transient
        le1_data.append([float(k), sum_log_r1 / valid_steps])
        le2_data.append([float(k), sum_log_r2 / valid_steps])

    return le1_data, le2_data


    """
    计算特定 K 值下的相图 (Phase Portrait)
    通常需要保存比分岔图更多的点来画出清晰的轨迹
    """
    x_traj = []
    y_traj = []
    
    x, y = 0.01, 0.01
    
    for n in range(iterations):
        x, y = _iter_system(x, y, a, k)
        
        if n >= iterations - keep_last:
            x_traj.append(x)
            y_traj.append(y)
            
    return x_traj, y_traj