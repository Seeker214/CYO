from fastapi import APIRouter, UploadFile, File, Form, Request
import shutil 
from cyo.services.chaos_algorithm import encryption, decryption
from cyo.utils.draw_frame import draw_frame
from cyo.utils.file_process import save_file, delete_file
from cyo.constants import SAVE_DIR, TARGETDETECTION, ENCRYPTION, DECRYPTION
import uuid
from pathlib import Path
import cv2 as cv
import json
import os
import logging

router = APIRouter()

@router.post("/api/predict")
async def target_detect(request: Request, 
                        file: UploadFile = File(...), 
                        image_category: str = Form(...)):
    temp_dir = "static/temp"
    path = Path(temp_dir)
    path.mkdir(parents=True, exist_ok=True)
    temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{file.filename}"

    try:
        save_file(file, temp_file_path)

        model = request.app.state.MODELS[image_category]
        detections = model.predict(img_path=temp_file_path, img_size=640)
        # TODO: draw predict frame and store image
        img_drawed_name = draw_frame(temp_file_path, detections, TARGETDETECTION)
        base_url = str(request.base_url).rstrip("/")
        return {
            "url": f"{base_url}/api/read_image/{TARGETDETECTION}/{img_drawed_name}",
        }
    finally:
        delete_file(temp_file_path)


@router.post("/api/encrypt")
async def image_encryption(request: Request, 
                           file: UploadFile, 
                           key: str = Form(...), 
                           image_category: str = Form(...)):
    temp_dir = "static/temp"
    path = Path(temp_dir)
    path.mkdir(parents=True, exist_ok=True)
    temp_name = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = f"{temp_dir}/{temp_name}"

    try:
        save_file(file, temp_file_path)

        model = request.app.state.MODELS[image_category]
        save_path = os.path.join(SAVE_DIR['encryption'], file.filename)
        save_path = save_path.split(".")[0] + ".png"
        logging.info(save_path)
        image_process_encryption(model=model, img_path=temp_file_path, save_path=save_path, key=key)
        base_url = str(request.base_url).rstrip("/")
        return {"url": f"{base_url}/api/read_image/{ENCRYPTION}/{file.filename.split('.')[0]}.png"}
    except Exception as e:
        logging.error(f"Encryption error: {e}")
        return {"error": str(e)} 
    finally:
        delete_file(temp_file_path)
    
@router.post("/api/decrypt")
async def image_decryption(request: Request, file: UploadFile, key: str = Form(...)):
    temp_dir = "static/temp"
    path = Path(temp_dir)
    path.mkdir(parents=True, exist_ok=True)
    temp_file_path = f"{temp_dir}/{uuid.uuid4()}_{file.filename}"

    try:
        save_file(file, temp_file_path)
        save_path = os.path.join(SAVE_DIR['decryption'], file.filename)
        image_process_decryption(img_path=temp_file_path, save_path=save_path, key=key)
        base_url = str(request.base_url).rstrip("/")
        return {"url": f"{base_url}/api/read_image/{DECRYPTION}/{file.filename.split('.')[0]}.png"}
    except KeyError:
        return {"error": KeyError}
    finally:
        delete_file(temp_file_path)

@router.get("/api/read_image/{image_category}/{image_name}")
async def read_image(image_category: str, image_name: str):
    image_path = os.path.join("static", image_category, image_name)
    if os.path.exists(image_path):
        return {"img_path": image_path}
    else:
        return {"error": "Image not found"}


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

