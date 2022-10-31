import http.server
import socketserver
import json
import pika
import time

from multiprocessing import Process


def runInParallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


def FileServer():
    PORT = 4321
    httpd = socketserver.TCPServer(
        ("", PORT), http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()


def Messenger():
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("Waiting for connection")
            time.sleep(5)

    channel.queue_declare(queue='ApiFileQ')

    def saveIncidentsBody(serialised_message):
        jSon = json.load(serialised_message)
        json.dump(jSon, write_file, indent=2)
        print("Traffic Incidents saved to disk")

    def callbackIncidents(ch, method, properties, body):
        try:
            saveIncidentsBody(body)
        except Exception as e:
            print("failed")

    channel.basic_consume(
        queue='ApiFileQ', on_message_callback=callbackIncidents, auto_ack=True)
    print(" I AM CONSUMING")
    channel.start_consuming()


if __name__ == "__main__":
    runInParallel(FileServer(), Messenger())
