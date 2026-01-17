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
        save_path = save_path.split(".")[0] + ".png"
        logging.info(save_path)
        image_process_encryption(model=model, img_path=temp_file_path, save_path=save_path, key=key)
        return {"success": "success"}
    except:
        return {"error": "error"}
    finally:
        delete_file(temp_file_path)
    
@router.post("/api/decrypt")
async def image_decryption(file: UploadFile, key: str):
    temp_dir = "static/temp"
    path = Path(temp_dir)
    path.mkdir(parents=True, exist_ok=True)
    temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{file.filename}"

    try:
        save_file(file, temp_file_path)
        save_path = os.path.join(SAVE_DIR['decryption'], file.filename)
        image_process_decryption(img_path=temp_file_path, save_path=save_path, key=key)
    except KeyError:
        return {"error": KeyError}
    finally:
        delete_file(temp_file_path)


def image_process_encryption(model, img_path, save_path, key):
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
        img[y1:y2, x1:x2, :] = encryption(img[y1:y2, x1:x2, :].copy(), key)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite(save_path, img, [cv.IMWRITE_PNG_COMPRESSION, 0])
    json_path = os.path.splitext(save_path)[0] + '.json'

    with open(json_path, 'w') as f:
        json.dump(coordinates, f)

def image_process_decryption(img_path, save_path, key):
    img = cv.imread(img_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    file_name = os.path.basename(save_path)
    coordinate_file_name = Path(file_name).stem + '.json'
    coordinate_file_path = os.path.join(SAVE_DIR['encryption'], coordinate_file_name)
    with open(coordinate_file_path, 'r') as f:
        coordinates = json.load(f)
    
    for co in reversed(coordinates):
        top = co['top']
        bottom = co['bottom']
        left = co['left']
        right = co['right']

        img[top:bottom, left:right, :] = decryption(img[top:bottom, left:right, :].copy(), key)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite(save_path, img)

