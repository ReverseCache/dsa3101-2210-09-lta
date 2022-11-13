import pika
import time


if __name__ == "__main__":
    # Connects ApiServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 10000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("ApiServer waiting for connection")
            time.sleep(5)

    channel.queue_declare(queue='ClientInterfaceQ')

    time.sleep(150)
    while True:
        channel.basic_publish(exchange="", routing_key="ClientInterfaceQ",
            properties=pika.BasicProperties(headers={'key': 'Incidents'}), body='')
        channel.basic_publish(exchange="", routing_key="ClientInterfaceQ",
            properties=pika.BasicProperties(headers={'key': 'Ltadump'}), body='')
        time.sleep(60)

