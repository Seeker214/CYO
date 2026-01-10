from fastapi import APIRouter, UploadFile, File, Form, Request
import shutil 
from cyo.services.chaos_algorithm import encryption, decryption
from cyo.utils.file_process import save_file, delete_file
from cyo.constants import SAVE_DIR
import uuid
from pathlib import Path
import cv2 as cv
import json
import os
import logging

router = APIRouter()

@router.post("/api/predict")
async def target_detect(request: Request, file: UploadFile = File(...)):
    temp_dir = "static/temp"
    path = Path(temp_dir)
    path.mkdir(parents=True, exist_ok=True)
    temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{file.filename}"

    try:
        save_file(file, temp_file_path)

        model = request.app.state.yolo_warship
        detections = model.predict(img_path=temp_file_path, img_size=640)
        # TODO: draw predict frame and store image
        return {
            "detect": detections
        }
    finally:
        delete_file(temp_file_path)


@router.post("/api/encrypt")
async def image_encryption(request: Request, file: UploadFile, key: str, category: str):
    temp_dir = "static/temp"
    path = Path(temp_dir)
    path.mkdir(parents=True, exist_ok=True)
    temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{file.filename}"

    try:
        save_file(file, temp_file_path)

        model = request.app.state.MODELS[category]
        save_path = os.path.join(SAVE_DIR['encryption'], file.filename)
        logging.info(save_path)
        image_process(model=model, img_path=temp_file_path, save_path=save_path, key=key)
        return {"success": "success"}
    except:
        return {"error": "error"}
    finally:
        delete_file(temp_file_path)
    

def image_process(model, img_path, save_path, key):
    img = cv.imread(img_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    detections = model.predict(img_path=img_path, img_size=640)
    coordinates = []
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        tmp = {
            'top': y1,
            'bottom': y2,
            'left': x1,
            'right': x2
        }
        coordinates.append(tmp)
        img[y1:y2, x1:x2, :] = encryption(img[y1:y2, x1:x2, :], key)

    cv.imwrite(save_path, img)
    json_path = os.path.splitext(save_path)[0] + '.json'

    with open(json_path, 'w') as f:
        json.dump(coordinates, f)

