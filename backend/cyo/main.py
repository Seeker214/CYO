from fastapi import FastAPI
from cyo.api import image_processing
from cyo.services.yolo_engine import YOLOEngine
from contextlib import asynccontextmanager
from cyo.constants import WARSHIP_MODEL_PATH, FACE_MODEL_PATH, CARID_MODEL_PATH

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

app.include_router(image_processing.router, prefix="", tags=["图像处理"])

