import pandas as pd
from traffic_images_api_call import get_json

def get_location():
    file_path = "./camera_data/"
    jsonObj = get_json()

    all_cameras_ids_locations = []
    camera_info = jsonObj["value"]
    for camera in camera_info:
        row = {}
        row["camera_id"] = camera["CameraID"]
        row["lat"] = camera["Latitude"]
        row["long"] = camera["Longitude"]
        all_cameras_ids_locations.append(row)
    all_cameras_df = pd.DataFrame(all_cameras_ids_locations)

    cameras_fname = "all_cameras_ids_locations.csv"
    all_cameras_df.to_csv(f"{file_path}{cameras_fname}", index = False)

if __name__ == "__main__":
    get_location()