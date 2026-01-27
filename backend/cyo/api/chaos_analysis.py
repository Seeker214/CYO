from fastapi import APIRouter, Body
from pydantic import BaseModel
from cyo.utils.chaos import compute_for_varying_k, compute_for_varying_a, calculate_phase_diagram
import numpy as np

router = APIRouter()

class ChaosRequest(BaseModel):
    mode: str = 'k'  # 'k' or 'a'
    start: float
    end: float
    step: float
    fixed_val: float 
    iterations: int = 5000
    phase_a: float = 0.6 
    phase_k: float = 0.8

@router.post("/api/chaos_analysis")
async def chaos_analysis(params: ChaosRequest = Body(...)):
    
    # 结果变量初始化
    axis_vals = []
    bif_x_flat = [] # 分岔图 X 坐标 (参数值)
    bif_y_flat = [] # 分岔图 Y 坐标 (系统状态 x)
    le1_vals = []
    le2_vals = []
    
    last_a = 0.0
    last_k = 0.0
    
    # --- 逻辑分流 ---
    if params.mode == 'k':
        # 调用：处理 K 变化
        axis_vals, bif_x_flat, bif_y_flat, le1_vals, le2_vals = compute_for_varying_k(
            a_fixed=params.fixed_val,
            k_start=params.start,
            k_end=params.end,
            step=params.step,
            iterations=params.iterations
        )
        # 记录最后一个点的参数用于画相图
        last_a = params.fixed_val
        last_k = axis_vals[-1]
        
    else:
        # 调用：处理 A 变化
        axis_vals, bif_x_flat, bif_y_flat, le1_vals, le2_vals = compute_for_varying_a(
            k_fixed=params.fixed_val,
            a_start=params.start,
            a_end=params.end,
            step=params.step,
            iterations=params.iterations
        )
        last_a = axis_vals[-1]
        last_k = params.fixed_val

    # --- 数据组装 (Format for Frontend) ---
    
    bif_data_formatted = np.column_stack((bif_x_flat, bif_y_flat)).tolist()
    
    # 2. 组装 Lyapunov (line data: [[x, y], ...])
    le1_data_formatted = np.column_stack((axis_vals, le1_vals)).tolist()
    le2_data_formatted = np.column_stack((axis_vals, le2_vals)).tolist()
    
    # 3. 计算末态相图 (额外调用一次单点迭代)
    phase_x, phase_y = calculate_phase_diagram(params.phase_a, 
                                               params.phase_k, 
                                               params.iterations)
    
    return {
        "status": "success",
        "data": {
            "mode": params.mode,
            "bifurcation": { 
                "x": bif_data_formatted 
            },
            "lyapunov": { 
                "le1": le1_data_formatted, 
                "le2": le2_data_formatted 
            },
            "phase": { 
                "title": f"Phase Diagram ({'k' if params.mode=='k' else 'a'}={axis_vals[-1]:.3f})",
                "x": phase_x, 
                "y": phase_y 
            }
        }
    }