import json
import pandas as pd
import urllib
import zipfile
from urllib.parse import urlparse
import httplib2 as http #External library

if __name__ == "__main__":
    file_path = "./camera_info/"
    # Authentication parameters
    headers = { 'AccountKey' : 'AO4qMbK3S7CWKSlplQZqlA==', 'accept' : 'application/json'} #this is by default

    # API parameters
    uri = 'http://datamall2.mytransport.sg/' #Resource URL
    path = 'ltaodataservice/Traffic-Imagesv2'
 
    # Build query string & specify type of API call
    target = urlparse(uri + path)
    print(target.geturl())
    method = 'GET'
    body = ''

    # Get handle to http
    h = http.Http()
    # Obtain results
    response, content = h.request(target.geturl(), method, body, headers)
    # Parse JSON to print
    jsonObj = json.loads(content)
    
    with open(f"{file_path}traffic_images_location.json", "w") as outfile:
        json.dump(jsonObj, outfile, sort_keys=True, indent=4, ensure_ascii=False)

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

##    selected_camera_ids = []
##    zip = zipfile.ZipFile(zip_name)
##    im_names = zip.namelist()
##    for name in im_names:
##        camera_id = name[:4]
##        selected_camera_ids.append(camera_id)
##    selected_cameras_df = all_cameras_df[all_cameras_df["camera_id"]
##                                         .isin(selected_camera_ids)]
##    selected_cameras_df.to_csv("selected_cameras_ids_locations.csv", index = False)

