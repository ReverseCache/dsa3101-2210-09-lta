import base64
import io
import json
import pika
import requests
import time

from datetime import datetime
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

# Predicts count and congestion from the lta_dump JSON
def get_predictions(input_payload):
    rainfalls = list(map(lambda x: x["rainfall"], input_payload))
    latitudes = list(map(lambda x: x["Latitude"], input_payload))
    longitudes = list(map(lambda x: x["Longitude"], input_payload))
    image_links = list(map(lambda x: x["ImageLink"], input_payload))

    input_images = []
    camera_ids = []
    images_datetime = []
    # image_strings = []

    for image_link in image_links:
        camera_id = image_link.split("/")[5].split("?")[0].split("_")[0]
        image_datetime = image_link.split("/")[5].split("?")[0].split("_")[2]
        image_datetime = datetime.strptime(image_datetime, '%Y%m%d%H%M%S')
        image_datetime = image_datetime.strftime('%Y/%m/%d %H.%M.%S')

        try:
            response = requests.get(image_link)
            img = Image.open(io.BytesIO(response.content))
            input_images.append(img)
            camera_ids.append(camera_id)
            images_datetime.append(image_datetime)
        except Exception as e:
            pass

    if input_images:
        count_results = count_model(input_images)
        congestion_results = congestion_model(input_images)

        count_vehicles = list(map(len, count_results.pandas().xyxy))
        congestions = list(map(lambda x: min(sum(x["name"] == "congested"), 1), congestion_results.pandas().xyxy))

        output_payload = {"rainfall": rainfalls, "latitude": latitudes, "longitude": longitudes, 
                "image_links": image_links, "camera_id": camera_ids, 
                "images_datetime": images_datetime, "count": count_vehicles, "congestion": congestions}

        return output_payload 

# Calls get_predictions() on the image, and send it to InterfaceServer
def callbackONE(channel, method, properties, body):
    print(" [InterfaceServer -> ModelServer] Received image")
    output_payload = get_prediction(body)
    message = json.dumps([output_payload])
    channel.basic_publish(exchange="", routing_key="ModelInterfaceQ", body=message)
    print(" [ModelServer -> InterfaceServer] Sent image_prediction JSON")

# Calls get_predictions() on the lta_dump JSON, and send it to FileServer
def callback87(channel, method, properties, body):
    print(" [ApiServer -> ModelServer] Received lta_dump JSON")
    output_payload = get_predictions(json.loads(json.loads(body)))
    message = json.dumps([output_payload])
    channel.basic_publish(exchange="", routing_key="ModelFileQ", body=message)
    print(" [ModelServer -> FileServer] Sent lta_dump_predictions JSON")


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

    # Receives image from InterfaceServer and send image_prediction JSON to InterfaceServer  
    channel.queue_declare(queue='InterfaceModelQ')
    channel.queue_declare(queue='ModelInterfaceQ')
    channel.basic_consume(on_message_callback = callbackONE, queue='InterfaceModelQ', auto_ack=True)

    # Receives lta_dump JSON from ApiServer and send lta_dump_predictions JSON to FileServer
    channel.queue_declare(queue='ApiModelQ')
    channel.queue_declare(queue='ModelFileQ')
    channel.basic_consume(on_message_callback = callback87, queue='ApiModelQ', auto_ack=True)

    channel.start_consuming()
