from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from cyo.utils.analysis import analyze_histogram, analyze_information_entropy, analyze_pixel_corelation
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

        return {
            "status": "success",
            "filename": file.filename,
            "data": {
                "histogram": histogram_data,   # 用于画折线图/柱状图
                "entropy": round(entropy_value, 5), # 用于展示数字
                "correlation": correlation_data # 用于画散点图
            }
        }

    except Exception as e:
        # 捕获其他异常
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))