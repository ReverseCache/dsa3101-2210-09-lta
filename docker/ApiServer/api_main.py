import httplib2 as http 
import json
import numpy as np
import pandas as pd
import pika
import requests
import time

from math import radians, cos, sin, asin, sqrt
from urllib.parse import urlparse

# Gets LTA dump and nearest incidents payload from the API
def get_payload():
    def haversine(lon1, lat1, lon2, lat2):

        # Converts decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # radius of earth in kilometers. Use 3956 for miles. Determines return value units.

        return c * r * 1000

    # Gets LTA camera id and images
    traffic_image_url = 'http://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2'
    headers_val = {'AccountKey': 'AO4qMbK3S7CWKSlplQZqlA=='}
    traffic_image_req = requests.get(url=traffic_image_url, headers=headers_val)
    traffic_image_df = pd.DataFrame(eval(traffic_image_req.content)['value'])

    # Gets LTA incidents on Expressways
    traffic_incidents_url = 'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents'
    traffic_incidents_req = requests.get(
        url=traffic_incidents_url, headers=headers_val)
    traffic_incidents_df = pd.DataFrame(eval(traffic_incidents_req.content)['value'])
    incidents_roads = ['AYE', 'BKE', 'CTE', 'ECP', 'KJE', 'KPE',
                       'MCE', 'PIE', 'SLE', 'TPE', 'Sentosa', 'Tuas', 'Woodlands']
    
    # Catches empty df
    try:
        traffic_incidents_df = (
            traffic_incidents_df[traffic_incidents_df['Message']
            .apply(lambda x: any(expressway in x for expressway in incidents_roads))]
        )
    except:
        pass

    # NEA API to get rainfall in mm
    weatherreq = requests.get(url='https://api.data.gov.sg/v1/environment/rainfall')
    weather_df = pd.DataFrame(eval(weatherreq.content)['metadata']['stations'])

    weather_df['latitude'] = weather_df['location'].apply(lambda x: x['latitude'])
    weather_df['longitude'] = weather_df['location'].apply(lambda x: x['longitude'])
    weather_df['timestamp'] = eval(weatherreq.content)['items'][0]['timestamp']
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

    station_rainfall = (
        pd.DataFrame(eval(weatherreq.content)['items'][0]['readings'])
        .rename(columns={'value': 'rainfall'})
    )

    weather_df = weather_df.merge(station_rainfall, how='left', left_on='id', right_on='station_id')
    weather_df = weather_df.drop(['id', 'device_id', 'station_id', 'location'], axis=1)

    # Calculations and table joining
    traffic_image_df['key'] = 0
    traffic_incidents_df['key'] = 0
    weather_df['key'] = 0

    # Selects incidents that occur within 500m of a camera location
    nearest_incidents = traffic_image_df.merge(traffic_incidents_df, 'outer', 'key')

    # Catches empty df
    try:
        nearest_incidents['incident_distance_from_id'] = (np.vectorize(haversine)(
            nearest_incidents['Latitude_x'], nearest_incidents['Longitude_x'], nearest_incidents['Latitude_y'], nearest_incidents['Longitude_y']))
        nearest_incidents = (
            nearest_incidents[nearest_incidents['incident_distance_from_id'] < 500]
            .sort_values('incident_distance_from_id')
        )
        nearest_incidents = nearest_incidents[['CameraID', 'Message']].sort_values('CameraID')
    except:
        pass

    # Selects nearest weather station for each camera id
    final_df = traffic_image_df.merge(weather_df, 'outer', 'key')
    final_df['distance_from_id'] = (np.vectorize(haversine)(
        final_df['Latitude'], final_df['Longitude'], final_df['latitude'], final_df['longitude']))
    final_df = (
        final_df
        .sort_values('distance_from_id')
        .groupby('CameraID')
        .head(1)[['CameraID', 'Latitude', 'Longitude', 'rainfall', 'ImageLink']]
    )
    final_df = final_df.sort_values('CameraID').reset_index(drop=True)

    # Converts dataframes to CSV to be used in frontend
    lta_dump_json = final_df.to_json(orient='records')
    incidents_data_json = nearest_incidents.to_json(orient='records')

    return lta_dump_json, incidents_data_json


if __name__ == "__main__":
    # Connects ApiServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("ApiServer waiting for connection")
            time.sleep(5)

    # Runs the API calls forever
    while True:
        lta_dump_json, incidents_data_json = get_payload()

        # Sends lta_dump JSON to ModelServer
        channel.queue_declare(queue='ApiModelQ')
        message = json.dumps(lta_dump_json)
        channel.basic_publish(exchange="", routing_key="ApiModelQ", body=message)
        print(" [APIServer -> ModelServer] Sent lta_dump JSON")

        # Sends incidents_data JSON to FileServer
        channel.queue_declare(queue='ApiFileQ')
        message = json.dumps(incidents_data_json)
        channel.basic_publish(exchange="", routing_key="ApiFileQ", body=message)
        print(" [APIServer -> FileServer] Sent incidents_data JSON")

        time.sleep(300)
    connection.close()