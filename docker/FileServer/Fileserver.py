import json
import pika
import time
from datetime import datetime

def saveIncidentsBody(serialised_message): #called
    j_data = json.loads(json.loads(serialised_message))
    # j_data = json.loads(serialised_message.decode('utf-8').replace("'", '"'))
    with open('j_data_file.json', 'w') as outfile:
        json.dump(j_data, outfile, indent=4)
    print("Traffic Incidents saved to disk") #called

def callbackIncidents(ch, method, properties, body):
    saveIncidentsBody(body)

def saveLta(serialised_message): #called
    j_data = json.loads(serialised_message.decode('utf-8').replace("'", '"'))
    # currentDateTime = datetime.now()
    with open("ltadump.json", 'w') as outfile:
        json.dump(j_data, outfile, indent=4)
    print("LTA dump saved to disk") #called

def callbackLta(ch, method, properties, body):
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
