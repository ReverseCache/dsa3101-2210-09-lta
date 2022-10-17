import os
import random
import shutil
from pathlib import Path

imagesDir = Path('./data/images')
imgList = list(imagesDir.iterdir())


# shuffling images
random.shuffle(imgList)
split = 0.2

rootnewdataDir = Path("./custom_dataset")

trainDir = rootnewdataDir / 'train'
try:
    trainDir.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print("Folder is already there")
else:
    print("Folder was created")

valDir = rootnewdataDir / 'val'
try:
    valDir.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print("Folder is already there")
else:
    print("Folder was created")

imgLen = len(imgList)
print("Images in total: ", imgLen)

train_images = imgList[: int(imgLen - (imgLen*split))]
val_images = imgList[int(imgLen - (imgLen*split)):]

print("Training images: ", len(train_images))
print("Validation images: ", len(val_images))

for imgName in train_images:
    print(imgName.name)
#     og_path = os.path.join('images', imgName)
#     target_path = os.path.join(train_path, imgName)

#     shutil.copyfile(og_path, target_path)

#     og_txt_path = os.path.join('bbox_txt', imgName.replace('.jpg', '.txt'))
#     target_txt_path = os.path.join(train_path, imgName.replace('.jpg', '.txt'))

#     shutil.copyfile(og_txt_path, target_txt_path)

# for imgName in val_images:
#     og_path = os.path.join('images', imgName)
#     target_path = os.path.join(val_path, imgName)

#     shutil.copyfile(og_path, target_path)

#     og_txt_path = os.path.join('bbox_txt', imgName.replace('.jpg', '.txt'))
#     target_txt_path = os.path.join(val_path, imgName.replace('.jpg', '.txt'))

#     shutil.copyfile(og_txt_path, target_txt_path)


# print("Done! ")
