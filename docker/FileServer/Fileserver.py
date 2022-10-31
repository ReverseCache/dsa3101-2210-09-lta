import http.server
import socketserver
import json
import pika
import time

#from threading import Thread


# def FileServer():
#     PORT = 4321
#     httpd = socketserver.TCPServer(
#         ("", PORT), http.server.SimpleHTTPRequestHandler)
#     print("Serving FileServer on port 4321")
#     httpd.serve_forever()


def Messenger():
    print("Starting Connection on FileServer!")
    Flag = True
    while Flag:
        try:
            print("Trying to connect with Rabbit")
            credentials = pika.PlainCredentials("guest", "guest")
            print("Credentials Success")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
            )
            print("Connection Success")
            channel = connection.channel()
            print("Channels Success")
            Flag = False
        except Exception as e:
            print("Waiting for connection")
            time.sleep(5)

    print("Connected on FileServer!")
    channel.queue_declare(queue='ApiFileQ')

    print("Declared Queue as \"ApiFileQ\" on FileServer!")

    def saveIncidentsBody(serialised_message):
        j_data = json.loads(serialised_message.decode(
            'utf-8').replace("'", '"'))
        with open('j_data_file.json', 'w') as outfile:
            json.dump(j_data, outfile, indent=4)
        print("Traffic Incidents saved to disk")

    def callbackIncidents(ch, method, properties, body):
        saveIncidentsBody(body)

    channel.basic_consume(
        queue='ApiFileQ', on_message_callback=callbackIncidents, auto_ack=True)
    print("I AM CONSUMING")
    channel.start_consuming()


if __name__ == "__main__":
    Messenger()
    # Thread(target=FileServer).start()
