import pika
import time
import pandas as pd
import json

def callbackInterfaceClient(channel, method, properties, body):
    # Sends image
    if properties.headers.get("key") == "ImagePrediction":
        # process json string (body) to json
        # json_file change to dataframe (now u hv the prediction jam and count)
        # output saved to a csv in FrontEnd with name ImagePrediction.csv
        with open("ImagePrediction.txt", "w") as text_file:
            text_file.write(body)
        pd.DataFrame(json.loads(body)[0]).rename(columns={'CameraID':'camera_id','Message':'message'}).to_csv('ImagePrediction.csv',index=False)

    # Sends incidents request
    elif properties.headers.get("key") == "Incidents":
        # process json string (body) to json
        # json_file to dataframe (if needed)
        # output saved to a csv in FrontEnd with name Incidents.csv
        with open("Incidents.txt", "w") as text_file:
            text_file.write(body)
        pd.DataFrame(json.loads(body)).to_csv('Incidents.csv',index=False)

    # Sends ltaDump request
    elif properties.headers.get("key") == "Ltadump":
        # first try: to read the Ltadump.csv 
        # error
        #process json string
        #etc
        # output saved to a csv in FrontEnd with name Ltadump.csv
        #  if theres no error then we append 
        with open("Ltadump.txt", "w") as text_file:
            text_file.write(body)
        res=[]
        input=json.loads(body)[0]
        for i,(date,dump) in enumerate(input.items()):
            temp=pd.DataFrame(dump[0])
            res.append(temp)
        res=pd.concat(res)
        res=res.merge(pd.read_csv('traffic_camera_region_roadname.csv',converters={'camera_id':str}),'left','camera_id')
        res=res[['camera_id','latitude','longitude','region','rainfall','image_links','roadname','count','congestion','images_datetime']]
        res.to_csv('Ltadump.csv',index=False)

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

    channel.queue_declare(queue='InterfaceClientQ')
    channel.basic_consume(queue='InterfaceClientQ', on_message_callback = callbackInterfaceClient, auto_ack=True)


    channel.start_consuming()