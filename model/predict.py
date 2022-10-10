import torch
import os
import zipfile
from PIL import Image

file_path = os.path.dirname(os.path.abspath(__file__))
images_path = file_path + "/images/"
sample_weights_path = file_path + "/sample_weights/"
model = torch.hub.load('ultralytics/yolov5', 'custom', path = sample_weights_path + 'sample_weight_640.pt') 

images = []

for zipped_file in os.listdir(images_path):
    with zipfile.ZipFile(images_path + os.path.basename(zipped_file)) as zf:
        for image_name in zf.namelist():
            image = Image.open(zf.open(image_name))
            images.append(image)

results = model(images)

results.print()

results.save()
