import torch
import os
import zipfile
from PIL import Image, ImageFile
from traffic_images_api_call import get_json
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime
# ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_prediction(image_link = None, real_time = True):
    file_path = os.path.dirname(os.path.abspath(__file__))
    weights_path = file_path + "/weights/"
    curr_datetime = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    images_output_path = file_path + "/images/output/"
    if not os.path.exists(images_output_path):
        os.makedirs(images_output_path)
        
    df_output_path = "{}{}.csv".format(images_output_path, curr_datetime)
    count_images_output_path = "{}{}/count/".format(images_output_path, curr_datetime)
    congestion_images_output_path = "{}{}/congestion/".format(images_output_path, curr_datetime)
    count_model = torch.hub.load('ultralytics/yolov5', 'custom', path = weights_path + 'count_best.pt')
    congestion_model = torch.hub.load('ultralytics/yolov5', 'custom', path = weights_path + 'congestion_best.pt')

    images = []
    camera_ids = []
    images_datetime = []

    if real_time:
        assert image_link is None

        jsonObj = get_json()
        camera_info = jsonObj["value"]
        i = 0

        for camera in camera_info:
            image_link = camera["ImageLink"]
            camera_id = image_link.split("/")[5].split("?")[0].split("_")[0]
            image_datetime = image_link.split("/")[5].split("?")[0].split("_")[2]
            image_datetime = datetime.strptime(image_datetime, '%Y%m%d%H%M%S')
            image_datetime = image_datetime.strftime('%Y/%m/%d %H.%M.%S')
            try:
                response = requests.get(image_link)
                img = Image.open(BytesIO(response.content))
                images.append(img)
                camera_ids.append(camera_id)
                images_datetime.append(image_datetime)
            except Exception as e:
                print(str(e))
            # break
            # i += 1
            # if i == 3:
            #     break

    else:
        assert image_link is not None

        images.append(image_link)
        camera_ids.append(image_link)
        images_datetime.append(image_link)
        
    
    if images:
        count_results = count_model(images)
        congestion_results = congestion_model(images)

        count_vehicles = list(map(len, count_results.pandas().xyxy))
        congestions = list(map(lambda x: min(sum(x["name"] == "congested"), 1), congestion_results.pandas().xyxy))
        print(congestion_results.pandas().xyxy)

        PIL_images_names = list(map(lambda x: "image{}".format(x), range(len(camera_ids))))
        df = pd.DataFrame({"camera_id": camera_ids, "PIL_image_name": PIL_images_names,
                        "images_datetime": image_datetime, "count": count_vehicles, "is_congested": congestions})
        df.to_csv(df_output_path, index = False)

        count_results.save(save_dir = count_images_output_path)
        congestion_results.save(save_dir = congestion_images_output_path)
        
    

if __name__ == "__main__":
    get_prediction()




# for zipped_file in os.listdir(images_path):
#     with zipfile.ZipFile(images_path + os.path.basename(zipped_file)) as zf:
#         for image_name in zf.namelist():
#             try:
#                 image = Image.open(zf.open(image_name))
#                 images.append(image)
#                 images_names.append(image_name)
#             except Exception as e:
#                 with open("error.txt", "a") as f:
#                     f.write("{} {} {}\n".format(zipped_file, image_name, str(e)))
#             break
#         break
        


# with open("success.txt", 'a') as f:
#     for image_name in images_names:
#         f.write("%s\n" % image_name)


# results = model(images)

# results.print()

# results.save()
