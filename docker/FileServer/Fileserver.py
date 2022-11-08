import json
import pika
import time
import os
from datetime import datetime, timedelta

def saveIncidentsBody(serialised_message): #called
    incidents_data = json.loads(json.loads(serialised_message))
    with open('incidents_data.json', 'w') as outfile:
        json.dump(incidents_data, outfile, indent=4)
    print("Traffic Incidents saved to disk")

def callbackIncidents(channel, method, properties, body):
    saveIncidentsBody(body)

def saveLta(serialised_message): #called
    ltadump = json.loads(serialised_message.decode('utf-8').replace("'", '"'))
    currentDateTime = datetime.now() + timedelta(hours = 8)
    currentDateTimeString = currentDateTime.strftime("%Y_%m_%d_%H_%M_%S")

    if not os.path.exists("ltadump/"):
        os.makedirs("ltadump/")

    with open(f"ltadump/{currentDateTimeString}.json", 'w') as outfile:
        json.dump(ltadump, outfile, indent=4)
    print("LTA dump saved to disk") #

def callbackLta(channel, method, properties, body):
    saveLta(body)


if __name__ == "__main__":
    print("Starting Connection on FileServer!")
    while True:
        try:
            print(1)
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            print(2)
            channel = connection.channel()
            break
        
        except Exception as e:
            print("Waiting for connection")
            time.sleep(5)

    channel.queue_declare(queue='ApiFileQ')
    channel.queue_declare(queue='ModelFileQ') 

    channel.basic_consume(queue='ModelFileQ', on_message_callback=callbackLta, auto_ack=True)
    channel.basic_consume(queue='ApiFileQ', on_message_callback=callbackIncidents, auto_ack=True)

    channel.start_consuming()
