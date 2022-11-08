import pika
import json
import time


def callbackClientInterface(channel, method, properties, body):
    if properties.headers.get("key") == "ImagePrediction":
        try:
            message = body
            channel.basic_publish(exchange="", routing_key="InterfaceModelQ",
                    properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)
            print(" [x] Sent bytes Body json to RabbitMQ")
        except Exception as e:
            print("failed to send message")
            print(str(e))
    elif properties.headers.get("key") == "Incidents":
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceFileQ",
                properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)
    elif properties.headers.get("key") == "Ltadump":
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceFileQ",
                properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)

def callbackModelInterface(channel, method, properties, body):
    with open('ImagePrediction.json', 'w') as outfile:
        json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
    
    message = body
    channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
            properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)

def callbackFileInterface(channel, method, properties, body):
    if properties.headers.get("key") == "Incidents":
        with open('incidents.json', 'w') as outfile:
            json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)

        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
                    properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)
    elif properties.headers.get("key") == "Ltadump":
        with open('ltadump.json', 'w') as outfile:
            json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)

        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
                    properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)

# def callbackGetImagePrediction(channel, method, properties, body):
#     '''
#     ASSUME BODY in bytes is serialised byte
#     '''
#     print(" [x] Received input" % body)
#     try:
#         message = body
#         channel.basic_publish(exchange="", routing_key="InterfaceModelQ",
#                 properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)
#         print(" [x] Sent bytes Body json to RabbitMQ")
#     except Exception as e:
#         print("failed to send message")
#         print(str(e))

# def callbackPostImagePrediction(channel, method, properties, body):
#     # Test if prediction succesfully reach interface
#     # pred = json.loads(json.loads(body))
#     with open('ImagePrediction.json', 'w') as outfile:
#         json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
    

#     message = body
#     channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
#                 properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)

# def callbackGetIncidents(channel, method, properties, body):
#     # Test if prediction succesfully reach interface
#     # pred = json.loads(json.loads(body))
#     # with open('prediction.json', 'w') as outfile:
#     #     json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
#     #

#     message = body
#     channel.basic_publish(exchange="", routing_key="InterfaceFileQ",
#                 properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)

# def callbackPostIncidents(channel, method, properties, body):
#     # Test if prediction succesfully reach interface
#     # pred = json.loads(json.loads(body))
#     with open('incidents.json', 'w') as outfile:
#         json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
#     #

#     message = body
#     channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
#                 properties=pika.BasicProperties(headers={'key': 'Incidents'}), body=message)

# def callbackGetLtadump(channel, method, properties, body):
#     # Test if prediction succesfully reach interface
#     # # pred = json.loads(json.loads(body))
#     # with open('prediction.json', 'w') as outfile:
#     #     json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
#     #

#     message = body
#     channel.basic_publish(exchange="", routing_key="InterfaceFileQ",
#                 properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)

# def callbackPostLtadump(channel, method, properties, body):
#     # Test if prediction succesfully reach interface
#     # pred = json.loads(json.loads(body))
#     with open('ltadump.json', 'w') as outfile:
#         json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
#     #

#     message = body
#     channel.basic_publish(exchange="", routing_key="InterfaceClientQ",
#                 properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body=message)

if __name__ == "__main__":
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            print(1)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            print(2)
            channel = connection.channel()
            break
        except Exception as e:
            print("Waiting for connection")
            time.sleep(5)

    channel.queue_declare(queue='ClientInterfaceQ')
    channel.queue_declare(queue='InterfaceClientQ')
    channel.queue_declare(queue='ModelInterfaceQ')
    channel.queue_declare(queue='InterfaceModelQ')
    channel.queue_declare(queue='InterfaceFileQ')
    channel.queue_declare(queue='FileInterfaceQ')

    channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackClientInterface, auto_ack=True)
    channel.basic_consume(queue='ModelInterfaceQ', on_message_callback = callbackModelInterface, auto_ack=True)
    channel.basic_consume(queue='FileInterfaceQ', on_message_callback = callbackFileInterface, auto_ack=True)

    with open("a", "w") as f:
        f.write("aa")
    
    # channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackGetImagePrediction, auto_ack=True)
    # channel.basic_consume(queue='ModelInterfaceQ', on_message_callback = callbackPostImagePrediction, auto_ack=True)
    # channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackGetIncidents, auto_ack=True)
    # channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackGetLtadump, auto_ack=True)
    # channel.basic_consume(queue='FileInterfaceQ', on_message_callback = callbackPostIncidents, auto_ack=True)
    # channel.basic_consume(queue='FileInterfaceQ', on_message_callback = callbackPostLtadump, auto_ack=True)

    channel.start_consuming()