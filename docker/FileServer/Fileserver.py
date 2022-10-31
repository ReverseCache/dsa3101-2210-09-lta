import http.server
import socketserver
import json
import pika


def FileServer():
    PORT = 4321

    httpd = socketserver.TCPServer(
        ("", PORT), http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    FileServer()

    credentials = pika.PlainCredentials("guest", "guest")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
    )
    channel = connection.channel()

    channel.queue_declare(queue='ApiFileQ')

    def saveIncidentsBody(serialised_message):
        with open('incidents.json', 'w', encoding='utf-8') as f:
            json.dump(json.load(serialised_message),
                      f, ensure_ascii=False, indent=4)
        print("Traffic Incidents saved to disk")

    def callbackIncidents(ch, method, properties, body):
        print(" [x] Received %r" % body)
        try:
            saveIncidentsBody(body)
        except Exception as e:
            print(e.message)

    channel.basic_consume(callbackIncidents, queue='ApiFileQ', no_ack=True)

    channel.start_consuming()
