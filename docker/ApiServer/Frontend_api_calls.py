import json
from urllib.parse import urlparse
import httplib2 as http  # External library

import torch


from threading import Timer

import pika

import requests
import pandas as pd
import numpy as np
import urllib.request


# Function to calculate distance given latitude and longitude

from numpy import radians, cos, sin, asin, sqrt


def get_json(path):
    # Authentication parameters
    headers = {'AccountKey': 'AO4qMbK3S7CWKSlplQZqlA==',
               'accept': 'application/json'}  # this is by default

    # API parameters
    uri = 'http://datamall2.mytransport.sg/ltaodataservice/'  # Resource URL
    #path = 'Traffic-Imagesv2'

    # Build query string & specify type of API call
    target = urlparse(uri + path)
    method = 'GET'
    body = ''

    # Get handle to http
    h = http.Http()
    # Obtain results
    response, content = h.request(target.geturl(), method, body, headers)
    # Parse JSON to print
    jsonObj = json.loads(content)
    return jsonObj


def payload():
    use_cuda = torch.cuda.is_available()
    if (use_cuda):
        # GPU accleration
        import cudf as pd
        print("GPU acceleration via rapids")
    else:
        # CPU
        import pandas as pd
        print("CPU fall back")

    def haversine(lon1, lat1, lon2, lat2):

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        r = 6371
        return c * r * 1000

    # Get LTA camera id and images

    traffic_image_url = 'http://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2'
    headers_val = {'AccountKey': 'AO4qMbK3S7CWKSlplQZqlA=='}
    traffic_image_req = requests.get(
        url=traffic_image_url, headers=headers_val)
    traffic_image_df = pd.DataFrame(eval(traffic_image_req.content)['value'])
    traffic_image_df['Count'] = np.random.uniform(
        low=0, high=20, size=(len(traffic_image_df.index),)).astype(int)
    traffic_image_df['is_jam'] = 0
    traffic_image_df = traffic_image_df.merge(pd.read_csv(
        'traffic_camera_region_roadname.csv', converters={'CameraID': str}), 'left', 'CameraID')
    traffic_image_df['RoadName'] = traffic_image_df['RoadName'] + \
        '_'+traffic_image_df['CameraID']

    # Get LTA incidents on Expressways

    traffic_incidents_url = 'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents'
    traffic_incidents_req = requests.get(
        url=traffic_incidents_url, headers=headers_val)
    traffic_incidents_df = pd.DataFrame(
        eval(traffic_incidents_req.content)['value'])
    incidents_roads = ['AYE', 'BKE', 'CTE', 'ECP', 'KJE', 'KPE',
                       'MCE', 'PIE', 'SLE', 'TPE', 'Sentosa', 'Tuas', 'Woodlands']
    traffic_incidents_df = traffic_incidents_df[traffic_incidents_df['Message'].apply(
        lambda x: any(expressway in x for expressway in incidents_roads))]

    # NEA API to get rainfall in mm

    weatherreq = requests.get(
        url='https://api.data.gov.sg/v1/environment/rainfall')
    weather_df = pd.DataFrame(eval(weatherreq.content)['metadata']['stations'])

    weather_df['latitude'] = weather_df['location'].apply(
        lambda x: x['latitude'])
    weather_df['longitude'] = weather_df['location'].apply(
        lambda x: x['longitude'])
    weather_df['timestamp'] = eval(weatherreq.content)['items'][0]['timestamp']
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

    station_rainfall = pd.DataFrame(eval(weatherreq.content)[
                                    'items'][0]['readings']).rename(columns={'value': 'rainfall'})

    weather_df = weather_df.merge(
        station_rainfall, how='left', left_on='id', right_on='station_id')
    weather_df = weather_df.drop(
        ['id', 'device_id', 'station_id', 'location'], axis=1)

    # Calculations and table joining

    traffic_image_df['key'] = 0
    traffic_incidents_df['key'] = 0
    weather_df['key'] = 0

    # Select incidents that occur within 500m of a camera location

    nearest_incidents = traffic_image_df.merge(
        traffic_incidents_df, 'outer', 'key')
    nearest_incidents['incident_distance_from_id'] = (np.vectorize(haversine)(
        nearest_incidents['Latitude_x'], nearest_incidents['Longitude_x'], nearest_incidents['Latitude_y'], nearest_incidents['Longitude_y']))
    nearest_incidents = nearest_incidents[nearest_incidents['incident_distance_from_id'] < 500].sort_values(
        'incident_distance_from_id')
    nearest_incidents = nearest_incidents[[
        'CameraID', 'Message']].sort_values('CameraID')

    # Select nearest weather station for each camera id

    final_df = traffic_image_df.merge(weather_df, 'outer', 'key')
    final_df['distance_from_id'] = (np.vectorize(haversine)(
        final_df['Latitude'], final_df['Longitude'], final_df['latitude'], final_df['longitude']))
    final_df = final_df.sort_values('distance_from_id').groupby('CameraID').head(
        1)[['CameraID', 'Latitude', 'Longitude', 'Region', 'rainfall', 'ImageLink', 'RoadName', 'Count', 'is_jam']]
    final_df = final_df.sort_values('CameraID').reset_index(drop=True)

    # Convert dataframes to CSV to be used in frontend

    ltaDump_json = final_df.to_json(orient='records')
    nearest_incidents_json = nearest_incidents.to_json(orient='records')

    return ltaDump_json, nearest_incidents_json


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


if __name__ == "__main__":

    def driver():
        ltaDump_json, nearest_incidents_json = payload()

        credentials = pika.PlainCredentials("guest", "guest")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
        )
        channel = connection.channel()

        # Fileservice dumps
        channel.queue_declare(queue='file_server')

        message = json.dumps(ltaDump_json)
        channel.basic_publish(
            exchange="", routing_key="file_server", body=message)
        print(" [x] Sent ltaDump json to RabbitMQ")

        message = json.dumps(nearest_incidents_json)
        channel.basic_publish(
            exchange="", routing_key="file_server", body=message)
        print(" [x] Sent nearest incidents json to RabbitMQ")

        channel.queue_declare(queue='model_server')
        message = json.dumps(traffic_images_json)
        channel.basic_publish(
            exchange="", routing_key="model_server", body=message)
        print(" [x] Sent traffic image data to RabbitMQ")
        connection.close()

    timer = RepeatTimer(300, driver)
    timer.start()
    # Runs hundred iterations before service shuts down
    time.sleep(300*100)
    timer.cancel()
