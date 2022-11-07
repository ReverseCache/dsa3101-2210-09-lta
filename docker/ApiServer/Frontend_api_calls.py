import json
from urllib.parse import urlparse
import httplib2 as http  # External library

# import torch


from threading import Timer
import time

import pika

import requests
import pandas as pd
import numpy as np
import urllib.request


# Function to calculate distance given latitude and longitude

from math import radians, cos, sin, asin, sqrt


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
    # use_cuda = torch.cuda.is_available()
    # if (use_cuda):
    #     # GPU accleration
    #     import cudf as pd
    #     print("GPU acceleration via rapids")
    # else:
    #     # CPU
    #     import pandas as pd
    #     print("CPU fall back")

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

    # Get LTA incidents on Expressways

    traffic_incidents_url = 'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents'
    traffic_incidents_req = requests.get(
        url=traffic_incidents_url, headers=headers_val)
    traffic_incidents_df = pd.DataFrame(
        eval(traffic_incidents_req.content)['value'])
    incidents_roads = ['AYE', 'BKE', 'CTE', 'ECP', 'KJE', 'KPE',
                       'MCE', 'PIE', 'SLE', 'TPE', 'Sentosa', 'Tuas', 'Woodlands']
    # to catch empty df
    try:
        traffic_incidents_df = traffic_incidents_df[traffic_incidents_df['Message'].apply(
            lambda x: any(expressway in x for expressway in incidents_roads))]
    except:
        pass

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

    # to catch empty df
    try:
        nearest_incidents['incident_distance_from_id'] = (np.vectorize(haversine)(
            nearest_incidents['Latitude_x'], nearest_incidents['Longitude_x'], nearest_incidents['Latitude_y'], nearest_incidents['Longitude_y']))
        nearest_incidents = nearest_incidents[nearest_incidents['incident_distance_from_id'] < 500].sort_values(
            'incident_distance_from_id')
        nearest_incidents = nearest_incidents[[
            'CameraID', 'Message']].sort_values('CameraID')
    except:
        pass

    # Select nearest weather station for each camera id
    final_df = traffic_image_df.merge(weather_df, 'outer', 'key')
    final_df['distance_from_id'] = (np.vectorize(haversine)(
        final_df['Latitude'], final_df['Longitude'], final_df['latitude'], final_df['longitude']))
    final_df = final_df.sort_values('distance_from_id').groupby('CameraID').head(
        1)[['CameraID', 'Latitude', 'Longitude', 'rainfall', 'ImageLink']]
    final_df = final_df.sort_values('CameraID').reset_index(drop=True)

    # Convert dataframes to CSV to be used in frontend

    ltaDump_json = final_df.to_json(orient='records')
    nearest_incidents_json = nearest_incidents.to_json(orient='records')

    return ltaDump_json, nearest_incidents_json


# class RepeatTimer(Timer):
#     def run(self):
#         while not self.finished.wait(self.interval):
#             self.function(*self.args, **self.kwargs)


if __name__ == "__main__":
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("Waiting for connection")
            time.sleep(5)

    def driver(channel):
        ltaDump_json, nearest_incidents_json = payload()

        # Api to Model queue
        channel.queue_declare(queue='ApiModelQ')

        message = json.dumps(ltaDump_json)
        channel.basic_publish(
            exchange="", routing_key="ApiModelQ", body=message) #success
        print(" [x] Sent ltaDump json to RabbitMQ") #called

        # Api to File queue
        channel.queue_declare(queue='ApiFileQ')

        message = json.dumps(nearest_incidents_json)
        channel.basic_publish(
            exchange="", routing_key="ApiFileQ", body=message) #success
        print(" [x] Sent nearest incidents json to RabbitMQ") #called

    for i in range(100):
        # timer = RepeatTimer(10, driver(channel))
        # timer.start()
        # Runs hundred iterations before service shuts down
        driver(channel)
        time.sleep(300)
        # timer.cancel()
    connection.close()
#Current problem with this API is the heartbeat: I added heartbeat = 1000 
#[error] <0.709.0> missed heartbeats from client, timeout: 60s
#pika.exceptions.StreamLostError: Stream connection lost: ConnectionResetError(104, 'Connection reset by peer')