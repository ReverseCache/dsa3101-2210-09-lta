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
    print("LTA dump saved to disk") #called

def callbackLta(channel, method, properties, body):
    saveLta(body)

def callbackInterfaceFile(channel, method, properties, body):
    if properties.headers.get("key") == "Incidents":
        if not os.path.exists("incidents_data.json"):
            channel.basic_publish(exchange="", routing_key="FileInterfaceQ",
                properties=pika.BasicProperties(headers={'key': 'Incidents'}), body='[]')

        f = open("incidents_data.json")
        message = json.dumps(json.load(f))
        channel.basic_publish(exchange="", routing_key="FileInterfaceQ",
                properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)

    elif properties.headers.get("key") == "Ltadump":
        if not os.path.exists("ltadump/"):
            channel.basic_publish(exchange="", routing_key="FileInterfaceQ",
                properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body='[]')

        FourtyMinsDateTime = datetime.now() + timedelta(hours = 8) - timedelta(minutes = 30)
        FourtyMinsDateTimeString = FourtyMinsDateTime.strftime("%Y_%m_%d_%H_%M_%S")
        
        last40MinsFiles = list(filter(lambda fileName: fileName >= FourtyMinsDateTimeString, os.listdir("ltadump/")))

        output_files = [{}]
        for fileName in last40MinsFiles:
            output_files[0][fileName] = json.load(open(f"ltadump/{fileName}"))

        message = json.dumps(output_files)
        channel.basic_publish(exchange="", routing_key="FileInterfaceQ",
                properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)

# def callbackPostIncidents(channel, method, properties, body):
#     if not os.path.exists("incidents_data.json"):
#         channel.basic_publish(exchange="", routing_key="FileInterfaceIncidentsQ", body='[]')

#     f = open("incidents_data.json")
#     message = json.dumps([json.load(f)])
#     channel.basic_publish(exchange="", routing_key="FileInterfaceIncidentsQ", body=message)

# def callbackPostLtadump(channel, method, properties, body):
#     if not os.path.exists("ltadump/"):
#         channel.basic_publish(exchange="", routing_key="FileInterfaceLtadumpQ", body='[]')

#     FourtyMinsDateTime = datetime.now() + timedelta(hours = 8) - timedelta(minutes = 30)
#     FourtyMinsDateTimeString = FourtyMinsDateTime.strftime("%Y_%m_%d_%H_%M_%S")
    
#     last40MinsFiles = list(filter(lambda fileName: fileName >= FourtyMinsDateTimeString, os.listdir("ltadump/")))

#     output_files = []
#     for fileName in last40MinsFiles:
#         output_files += json.load(open(f"ltadump/{fileName}"))

#     message = json.dumps(output_files)
#     channel.basic_publish(exchange="", routing_key="FileInterfaceLtadumpQ", body=message)


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
    channel.queue_declare(queue='InterfaceFileQ')
    channel.queue_declare(queue='FileInterfaceQ')

    channel.basic_consume(queue='ModelFileQ', on_message_callback=callbackLta, auto_ack=True)
    channel.basic_consume(queue='ApiFileQ', on_message_callback=callbackIncidents, auto_ack=True)
    channel.basic_consume(queue='InterfaceFileQ', on_message_callback=callbackInterfaceFile, auto_ack=True)

    channel.start_consuming()
