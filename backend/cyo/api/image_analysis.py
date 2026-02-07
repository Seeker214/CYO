from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from cyo.utils.analysis import analyze_histogram, analyze_information_entropy, analyze_pixel_corelation, calculate_npcr_uaci
from cyo.services.chaos_algorithm import encryption
from cyo.constants import ENCRYPTION, SAVE_DIR
import json
from pathlib import Path
import os

router = APIRouter()

@router.post("/api/analyze_image")
async def analyze_image(file: UploadFile = File(...), is_encrypted: bool = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        
        nparr = np.frombuffer(contents, np.uint8)
        # cv2.imdecode 将一维数组解码为图像格式 (H, W, C)
        # cv2.IMREAD_COLOR 读取彩色图 (BGR 格式)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if is_encrypted:
            coordinates_file_name = Path(file.filename).stem + '.json'
            coordinates_file_path = os.path.join(SAVE_DIR['encryption'], coordinates_file_name)
            with open(coordinates_file_path, 'r') as f:
                coordinates = json.load(f)

            top = coordinates[0]['top']
            bottom = coordinates[0]['bottom']
            left = coordinates[0]['left']
            right = coordinates[0]['right']
            image = image[top:bottom, left:right].copy()

        if image is None:
             raise HTTPException(status_code=400, detail="Could not decode image")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
        
        histogram_data = analyze_histogram(image)
        entropy_value = analyze_information_entropy(image)
        correlation_data = analyze_pixel_corelation(image, sample_size=3000)
        
        # 差分攻击分析（仅在明文图像时进行）
        differential_data = None
        if not is_encrypted:
            try:
                # 生成两个仅有一个像素差异的测试图像
                img1 = image.copy()
                img2 = image.copy()
                
                # 将图像调整为 240x256，确保置乱过程充分执行
                # gcd(240, 256) = 16，置乱循环会执行 240 次（而 256x256 只执行 1 次）
                img1 = cv2.resize(img1, (256, 240))
                img2 = cv2.resize(img2, (256, 240))
                
                # 修改一个像素值，避免 uint8 溢出
                original_val = int(img2[0, 0, 0])
                img2[0, 0, 0] = (original_val + 1) % 256
                
                # 使用固定密钥加密这两个图像
                key = "0.1, 0.1"
                enc_img1 = encryption(img1, key)
                enc_img2 = encryption(img2, key)
                
                # 计算加密后图像的差分指标
                npcr, uaci = calculate_npcr_uaci(enc_img1, enc_img2)
                differential_data = {
                    "npcr": round(npcr, 4),
                    "uaci": round(uaci, 4),
                    "npcr_ideal": 99.6094,
                    "uaci_ideal": 33.4635
                }
            except Exception as e:
                print(f"差分攻击分析失败: {e}")
                import traceback
                traceback.print_exc()

        return {
            "status": "success",
            "filename": file.filename,
            "data": {
                "histogram": histogram_data,   # 用于画折线图/柱状图
                "entropy": round(entropy_value, 5), # 用于展示数字
                "correlation": correlation_data, # 用于画散点图
                "differential": differential_data # 差分攻击指标
            }
        }

    except Exception as e:
        # 捕获其他异常
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))