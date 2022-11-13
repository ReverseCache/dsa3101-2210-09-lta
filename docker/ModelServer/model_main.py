import base64
import io
import json
import pika
import time

from PIL import Image, ImageFile
from segmentation import get_count_model, get_congestion_model
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Predicts count and congestion from a single image
def get_prediction(file):
    input_image = Image.open(io.BytesIO(base64.b64decode(file)))
    count_result = count_model(input_image)
    congestion_result = congestion_model(input_image)

    count_vehicles = list(map(len, count_result.pandas().xyxy))
    congestions = list(map(lambda x: min(sum(x["name"] == "congested"), 1), congestion_result.pandas().xyxy))

    output_payload = {"count": count_vehicles,
                      "congestion": congestions}

    return output_payload

# Calls get_prediction() on the image, and send it to InterfaceServer
def callbackONE(channel, method, properties, body):
    print(" [InterfaceServer -> ModelServer] Received image")
    output_payload = get_prediction(body)
    message = json.dumps([output_payload])
    channel.basic_publish(exchange="", routing_key="ModelInterfaceQ", body=message)
    print(" [ModelServer -> InterfaceServer] Sent image_prediction JSON")


if __name__ == "__main__":
    # Retrieves count and congestion model
    count_model = get_count_model()
    congestion_model = get_congestion_model()

    # Connects ModelServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("ModelServer waiting for connection")
            time.sleep(5)

    # Receives image from InterfaceServer and sends image_prediction JSON to InterfaceServer  
    channel.queue_declare(queue='InterfaceModelQ')
    channel.queue_declare(queue='ModelInterfaceQ')
    channel.basic_consume(on_message_callback = callbackONE, queue='InterfaceModelQ', auto_ack=True)

    channel.start_consuming()
