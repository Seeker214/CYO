import pytest
from cyo.services.chaos_algorithm import encryption, decryption
from cyo.services.yolo_engine import YOLOEngine
from PIL import Image
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np


@pytest.mark.parametrize("image_path, key, model_path", [
    ("static/000018.jpg", '0.1,0.1', "models/CelebA.onnx"),
    ("static/100001270.jpg", '0.1,0.1', "models/HRSC2016.onnx"),
    ("static/36.jpg", '0.1,0.1', "models/CCPD.onnx"),
])
def test_image_encrypt_and_decrypt(image_path, key, model_path):

    # image = Image.open(image_path)
    image = cv.imread(image_path)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    yolo = YOLOEngine(model_path=model_path)
    detections = yolo.predict(img_path=image_path)
    image_en = image.copy()
    for det in detections:
        left, top, right, bottom = det['bbox']
        image_en[top:bottom, left:right, :] = encryption(image_en[top:bottom, left:right, :].copy(), key)

    # image_en = Image.fromarray(image_en)
    plt.subplot(1, 2, 1)
    plt.imshow(image_en)
    # plt.show()

    # image_en = np.array(image_en)
    image_de = image_en.copy()
    for det in reversed(detections):
        left, top, right, bottom = det['bbox']
        image_de[top:bottom, left:right, :] = decryption(image_de[top:bottom, left:right, :].copy(), key)

    # image_de = Image.fromarray(image_de)
    plt.subplot(1, 2, 2)
    plt.imshow(image_de)
    plt.show()

