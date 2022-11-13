import json
import os
import pika
import time

from datetime import datetime, timedelta

# Saves incidents_data JSON
def save_incidents(file):
    with open('incidents_data.json', 'w') as outfile:
        json.dump(file, outfile, indent=4)

# Saves lta_dump_predictions JSON
def save_lta(file):
    currentDateTime = datetime.now() + timedelta(hours = 8)
    currentDateTimeString = currentDateTime.strftime("%Y_%m_%d_%H_%M_%S")
    if not os.path.exists("lta_dump_predictions/"):
        os.makedirs("lta_dump_predictions/")
    with open(f"lta_dump_predictions/{currentDateTimeString}.json", 'w') as outfile:
        json.dump(file, outfile, indent=4)

# Calls save_incidents() on the nearest_incidents JSON
def callbackIncidents(channel, method, properties, body):
    print(" [ApiServer -> FileServer] Received incidents_data JSON")
    incidents_data = json.loads(json.loads(body))
    save_incidents(incidents_data)

# Calls save_lta() on the lta_dump_predictions JSON
def callbackLta(channel, method, properties, body):
    print(" [ModelServer -> FileServer] Received lta_dump_predictions JSON")
    lta_dump_predictions = json.loads(body.decode('utf-8').replace("'", '"'))
    save_lta(lta_dump_predictions)
    
# Sends JSON file InterfaceServer
def callbackInterfaceFile(channel, method, properties, body):
    # Sends incidents_data JSON
    if properties.headers.get("key") == "Incidents":
        print(" [InterfaceServer -> FileServer] Received incidents request")
        # Sends incidents_data JSON otherwise
        if os.path.exists("incidents_data.json"):
            f = open("incidents_data.json")
            message = json.dumps(json.load(f))
            channel.basic_publish(exchange="", routing_key="FileInterfaceQ",
                properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)
            print(" [InterfaceServer -> FileServer] Sends incidents_data JSON")

    # Sends 40_mins_lta_dump_predictions JSON
    elif properties.headers.get("key") == "Ltadump":
        print(" [InterfaceServer -> FileServer] Received ltaDump request")
        # Sends the 40_mins_lta_dump_predictions JSON otherwise
        if os.path.exists("lta_dump_predictions/"):
            FourtyMinsDateTime = datetime.now() + timedelta(hours = 8) - timedelta(minutes = 40)
            FourtyMinsDateTimeString = FourtyMinsDateTime.strftime("%Y_%m_%d_%H_%M_%S")
            last40MinsFiles = list(filter(lambda fileName: fileName >= FourtyMinsDateTimeString, os.listdir("lta_dump_predictions/")))

            output_files = [{}]
            for fileName in last40MinsFiles:
                output_files[0][fileName] = json.load(open(f"lta_dump_predictions/{fileName}"))

            message = json.dumps(output_files)
            channel.basic_publish(exchange="", routing_key="FileInterfaceQ",
                properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)
            print(" [InterfaceServer -> FileServer] Sends 40_mins_lta_dump_predictions JSON")


if __name__ == "__main__":
    # Connects FileServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 10000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("FileServer waiting for connection")
            time.sleep(5)

    # Receives incidents_data JSON from ApiServer
    channel.queue_declare(queue='ApiFileQ')
    channel.basic_consume(queue='ApiFileQ', on_message_callback=callbackIncidents, auto_ack=True)

    # Receives lta_dump_predictions JSON from ModelServer
    channel.queue_declare(queue='ModelFileQ') 
    channel.basic_consume(queue='ModelFileQ', on_message_callback=callbackLta, auto_ack=True)

    # Receives message from InterfaceServer and sends JSON file to InterfaceServer
    channel.queue_declare(queue='InterfaceFileQ')
    channel.queue_declare(queue='FileInterfaceQ')
    channel.basic_consume(queue='InterfaceFileQ', on_message_callback=callbackInterfaceFile, auto_ack=True)

    channel.start_consuming()
