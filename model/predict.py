import torch
import os
import zipfile
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

file_path = os.path.dirname(os.path.abspath(__file__))
images_path = file_path + "/images/"
sample_weights_path = file_path + "/sample_weights/"
model = torch.hub.load('ultralytics/yolov5', 'custom', path = sample_weights_path + 'best_640.pt') 

images = []
images_names = []

for zipped_file in os.listdir(images_path):
    # if zipped_file >= "2022_01_05_12" and zipped_file <= "2022_01_05_12_30_00":
    with zipfile.ZipFile(images_path + os.path.basename(zipped_file)) as zf:
        for image_name in zf.namelist():
            try:
                image = Image.open(zf.open(image_name))
                images.append(image)
                images_names.append(image_name)
            except Exception as e:
                with open("error.txt", "a") as f:
                    f.write("{} {} {}\n".format(zipped_file, image_name, str(e)))
            break
        break
        


with open("success.txt", 'a') as f:
    for image_name in images_names:
        f.write("%s\n" % image_name)


results = model(images)

results.print()

results.save()
