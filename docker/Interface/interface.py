import pika
import json
import time


def callbackONE(ch, method, properties, body):
    print(" [x] Received %r" % body)
    try:
        '''
        ASSUME BODY in bytes is serialised byte
        '''

        credentials = pika.PlainCredentials("guest", "guest")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
        )
        channel = connection.channel()
        # Api to Model queue
        channel.queue_declare(queue='InterfaceModelQ')

        message = body

        channel.basic_publish(
            exchange="", routing_key="InterfaceModelQ", body=message)
        print(" [x] Sent bytes Body json to RabbitMQ")
        connection.close()

    except Exception as e:
        print("failed to send message")
        print(str(e))

if __name__ == "__main__":
    credentials = pika.PlainCredentials("guest", "guest")
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
            )
            break
        except Exception as e:
            print(str(e))
            time.sleep(10)

    channel = connection.channel()

    channel.queue_declare(queue='ClientInterfaceQ')

    channel.basic_consume(queue='ClientInterfaceQ', on_message_callback = callbackONE, auto_ack=True)

    channel.start_consuming()

    channel.queue_declare(queue='InterfaceModelQ')

    channel.basic_consume(queue='InterfaceModelQ', on_message_callback = callbackONE, auto_ack=True)

    channel.start_consuming()
