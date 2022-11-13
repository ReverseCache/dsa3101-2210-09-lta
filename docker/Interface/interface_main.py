import json
import pika
import time

# Sends message to ModelServer or FileServer
def callbackClientInterface(channel, method, properties, body):
    # Sends image
    if properties.headers.get("key") == "ImagePrediction":
        print(" [ClientServer -> InterfaceServer] Received image")
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceModelQ",
            properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)
        print(" [InterfaceServer -> ModelServer] Sent image")

    # Sends incidents request
    elif properties.headers.get("key") == "Incidents":
        print(" [ClientServer -> InterfaceServer] Received incidents request")
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceFileQ",
            properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)
        print(" [InterfaceServer -> FileServer] Sent incidents request")

    # Sends ltaDump request
    elif properties.headers.get("key") == "Ltadump":
        print(" [ClientServer -> InterfaceServer] Received ltaDump request")
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceFileQ",
            properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)
        print(" [InterfaceServer -> FileServer] Sent ltaDump request")

# Sends image_prediction JSON to ClientServer
def callbackModelInterface(channel, method, properties, body):
    print(" [ModelServer -> InterfaceServer] Received image_prediction JSON")
    with open('ImagePrediction.json', 'w') as outfile:
        json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
    message = body
    channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
        properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)
    print(" [InterfaceServer -> ClientServer] Sent image_prediction JSON")

# Sends JSON file to ClientServer
def callbackFileInterface(channel, method, properties, body):
    # Sends incidents_data JSON
    if properties.headers.get("key") == "Incidents":
        print(" [FileServer -> InterfaceServer] Received incidents_data JSON")
        with open('incidents.json', 'w') as outfile:
            json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
            properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)
        print(" [InterfaceServer -> ClientServer] Sent incidents_data JSON")

    # Sends 40_mins_lta_dump_predictions JSON
    elif properties.headers.get("key") == "Ltadump":
        print(" [FileServer -> InterfaceServer] Received 40_mins_lta_dump_predictions JSON")
        with open('ltadump.json', 'w') as outfile:
            json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
            properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)
        print(" [InterfaceServer -> ClientServer] Sent 40_mins_lta_dump_predictions JSON")


if __name__ == "__main__":
    # Connects InterfaceServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 10000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("InterfaceServer waiting for connection")
            time.sleep(5)

    # Receives message from ClientServer and sends it to ModelServer or FileServer
    channel.queue_declare(queue='ClientInterfaceQ')
    channel.queue_declare(queue='InterfaceModelQ')
    channel.queue_declare(queue='InterfaceFileQ')
    channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackClientInterface, auto_ack=True)

    # Receives JSON file from ModelServer or FileServer and sends it to ClientServer
    channel.queue_declare(queue='ModelInterfaceQ')
    channel.queue_declare(queue='InterfaceClientQ')
    channel.queue_declare(queue='FileInterfaceQ')
    channel.basic_consume(queue='ModelInterfaceQ', on_message_callback = callbackModelInterface, auto_ack=True)
    channel.basic_consume(queue='FileInterfaceQ', on_message_callback = callbackFileInterface, auto_ack=True)

    channel.start_consuming()