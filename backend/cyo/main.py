from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from cyo.api import image_processing, image_analysis
from cyo.services.yolo_engine import YOLOEngine
from contextlib import asynccontextmanager
from cyo.constants import (WARSHIP_MODEL_PATH, FACE_MODEL_PATH, CARID_MODEL_PATH, 
                            TARGETDETECTION, ENCRYPTION, DECRYPTION, SAVE_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.MODELS = {
        "warship": YOLOEngine(model_path=WARSHIP_MODEL_PATH),
        "face": YOLOEngine(model_path=FACE_MODEL_PATH),
        "car": YOLOEngine(model_path=CARID_MODEL_PATH),
    }
    yield
    del app.state.MODELS

app = FastAPI(
    title="CYO",
    description="基于改进YOLOv9的敏感区域图像加密算法",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境请指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(f"/api/read_image/{TARGETDETECTION}", StaticFiles(directory=SAVE_DIR['detection']))
app.mount(f"/api/read_image/{ENCRYPTION}", StaticFiles(directory=SAVE_DIR['encryption']))
app.mount(f"/api/read_image/{DECRYPTION}", StaticFiles(directory=SAVE_DIR['decryption']))

app.include_router(image_processing.router, prefix="", tags=["图像处理"])
app.include_router(image_analysis.router, prefix="", tags=["图像分析"])

