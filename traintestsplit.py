import random
from pathlib import Path

textDir = Path('./data/bbox_txt')
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

for path_img in train_images:
    base = path_img.name
    dest = trainDir / base
    path_img.rename(dest)

    path_text = textDir / (path_img.stem + ".txt")
    base_txt = path_text.name
    dest = trainDir / base_txt
    path_text.rename(dest)
#     og_txt_path = os.path.join('bbox_txt', imgName.replace('.jpg', '.txt'))
#     target_txt_path = os.path.join(train_path, imgName.replace('.jpg', '.txt'))

#     shutil.copyfile(og_txt_path, target_txt_path)

for path_img in val_images:
    base = path_img.name
    dest = valDir / base
    path_img.rename(dest)

    path_text = textDir / (path_img.stem + ".txt")
    base_txt = path_text.name
    dest = valDir / base_txt
    path_text.rename(dest)
#     target_path = os.path.join(val_path, imgName)

#     shutil.copyfile(og_path, target_path)

#     og_txt_path = os.path.join('bbox_txt', imgName.replace('.jpg', '.txt'))
#     target_txt_path = os.path.join(val_path, imgName.replace('.jpg', '.txt'))

#     shutil.copyfile(og_txt_path, target_txt_path)


print("Completed!")
