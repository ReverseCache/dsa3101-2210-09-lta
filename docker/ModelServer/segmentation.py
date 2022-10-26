import torch
from PIL import Image
import io

def get_count_model():
    model = torch.hub.load('./yolov5', 'custom', path='./model/count_best.pt', source='local')
    return model

def get_congestion_model():
    model = torch.hub.load('./yolov5', 'custom', path='./model/congestion_best.pt', source='local')
    return model

def get_image_from_bytes(binary_image):
    return Image.open(io.BytesIO(binary_image))