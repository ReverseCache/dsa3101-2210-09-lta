import requests
import pandas as pd
import numpy as np
import urllib.request

# GPU accleration
import cudf

if __name__ == "__main__":
    # Traffic Image
    traffic_image_url = 'http://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2'
    headers_val = {'AccountKey': 'AO4qMbK3S7CWKSlplQZqlA=='}
    traffic_image_req = requests.get(
        url=traffic_image_url, headers=headers_val)
    traffic_image_df = pd.DataFrame(eval(traffic_image_req.content)['value'])

    # Traffic Speed
    traffic_speed_url = 'http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBandsv2'
    traffic_speed_req = requests.get(
        url=traffic_speed_url, headers=headers_val)
    traffic_speed_df = pd.DataFrame(eval(traffic_speed_req.content)['value'])

    # Traffic incidents
    traffic_incidents_url = 'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents'
    traffic_incidents_req = requests.get(
        url=traffic_incidents_url, headers=headers_val)
    traffic_incidents_df = pd.DataFrame(
        eval(traffic_incidents_req.content)['value'])

    def location_splitter(location):
        location = location.split(' ')
        return location[0], location[1], location[2], location[3]

    traffic_speed_df['start_latitude'], traffic_speed_df['start_longitude'], traffic_speed_df['end_latitude'], traffic_speed_df['end_longitude'] = np.vectorize(
        location_splitter)(traffic_speed_df['Location'])

    # Weather APi
    weatherreq = requests.get(
        url='https://api.data.gov.sg/v1/environment/rainfall')

    new_weather_df = pd.DataFrame(eval(weatherreq.content)[
                                  'metadata']['stations'])

    new_weather_df['latitude'] = new_weather_df['location'].apply(
        lambda x: x['latitude'])
    new_weather_df['longitude'] = new_weather_df['location'].apply(
        lambda x: x['longitude'])
    new_weather_df['timestamp'] = eval(weatherreq.content)[
        'items'][0]['timestamp']
    new_weather_df['timestamp'] = pd.to_datetime(new_weather_df['timestamp'])

    station_rainfall = pd.DataFrame(eval(weatherreq.content)[
                                    'items'][0]['readings']).rename(columns={'value': 'rainfall in mm'})

    new_weather_df = new_weather_df.merge(
        station_rainfall, how='left', left_on='id', right_on='station_id')
    new_weather_df = new_weather_df.drop(
        ['id', 'device_id', 'station_id', 'location'], axis=1)

    onemapTokenAPIResponse = requests.post('https://developers.onemap.sg/privateapi/auth/post/getToken', json={
        'email': 'leejin@u.nus.edu', 'password': 'Whysohardtochange123!'})  # .content
    onemapAPItoken = eval(onemapTokenAPIResponse.content)['access_token']
    onemapResponse = requests.get('https://developers.onemap.sg/privateapi/commonsvc/revgeocode?location=%s,%s&token=%s&buffer=100&addressType=all' %
                                  (str(1.32311), str(103.76714), onemapAPItoken))

    def roadnamegrabber(name, latitude, longitude):
        if name[0] == 'S' and len(name) < 5:
            tempResponse = requests.get('https://developers.onemap.sg/privateapi/commonsvc/revgeocode?location=%s,%s&token=%s&buffer=100&addressType=all' %
                                        (str(latitude), str(longitude), onemapAPItoken))
            name = pd.DataFrame(eval(tempResponse.content)[
                                'GeocodeInfo'])['ROAD'].mode()[0]
        return name

    new_weather_df['name'] = np.vectorize(roadnamegrabber)(
        new_weather_df['name'], new_weather_df['latitude'], new_weather_df['longitude'])

    # Requiured Payload
    traffic_image_df.to_csv('traffic_image.csv', index=False)
    traffic_speed_df.to_csv('traffic_speed.csv', index=False)
    traffic_incidents_df.to_csv('traffic_incidents.csv', index=False)
    new_weather_df.to_csv('weather.csv', index=False)
