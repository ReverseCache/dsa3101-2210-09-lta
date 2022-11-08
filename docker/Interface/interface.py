import pika
import json
import time


def callbackONE(channel, method, properties, body):
    '''
    ASSUME BODY in bytes is serialised byte
    '''
    print(" [x] Received input" % body)
    try:
        message = body
        channel.basic_publish(exchange="", routing_key="InterfaceModelQ", body=message)
        print(" [x] Sent bytes Body json to RabbitMQ")
    except Exception as e:
        print("failed to send message")
        print(str(e))

def callbackShow(channel, method, properties, body):
    # Test if prediction succesfully reach interface
    # pred = json.loads(json.loads(body))
    with open('prediction.json', 'w') as outfile:
        json.dump(json.loads(body.decode('utf-8').replace("'", '"')), outfile, indent=4)
    #

    message = body
    channel.basic_publish(exchange="", routing_key="InterfaceClientQ", body=message)

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
    channel.queue_declare(queue='InterfaceModelQ')
    channel.queue_declare(queue='ModelInterfaceQ')
    channel.queue_declare(queue='InterfaceClientQ')

    channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackONE, auto_ack=True)
    channel.basic_consume(queue='ModelInterfaceQ', on_message_callback = callbackShow, auto_ack=True)

    channel.start_consuming()