import base64
from ssl import CHANNEL_BINDING_TYPES
from segmentation import get_count_model, get_congestion_model, get_image_from_bytes
import io
from PIL import Image
import json
from datetime import datetime
import requests
import pika
import time

#def get_prediction(file: bytes = File(...)):
def get_prediction(file):
    print("get_prediction")
    input_image = get_image_from_bytes(file)
    count_result = count_model(input_image)
    count_result.render()

    congestion_result = congestion_model(input_image)
    congestion_result.render()

    count_vehicles = list(map(len, count_result.pandas().xyxy))
    congestions = list(map(lambda x: min(
            sum(x["name"] == "congested"), 1), congestion_result.pandas().xyxy))

    bytes_io = io.BytesIO()
    img_base64 = Image.fromarray(count_result.ims[0])
    img_base64.save(bytes_io, format="jpeg")
    img_string = base64.b64encode(bytes_io.getvalue())
    count_img_strings = [img_string]

    bytes_io = io.BytesIO()
    img_base64 = Image.fromarray(congestion_result.ims[0])
    img_base64.save(bytes_io, format="jpeg")
    img_string = base64.b64encode(bytes_io.getvalue())
    congestion_img_strings = [img_string]

    # Image.open(io.BytesIO(base64.b64decode(img_string))) # to build Image
    # return Response(content = io.BytesIO(base64.b64decode(img_string)).getvalue(), media_type = "image/jpeg")

    output_payload = {"count_img_strings": count_img_strings,
                      "congestion_img_strings": congestion_img_strings,
                      "count": count_vehicles,
                      "congestion": congestions}
    return output_payload

#def get_predictions(input_payload: dict = Body(...)):
def get_predictions(input_payload):
    print("get_predictions")
    image_links = list(map(lambda x: x["ImageLink"], input_payload["value"]))
    input_images = []
    camera_ids = []
    images_datetime = []
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
            break #remove this
        except Exception as e:
            print(str(e))

    if input_images:
        count_results = count_model(input_images)
        count_results.render()

        congestion_results = congestion_model(input_images)
        congestion_results.render()

        count_vehicles = list(map(len, count_results.pandas().xyxy))
        congestions = list(map(lambda x: min(
            sum(x["name"] == "congested"), 1), congestion_results.pandas().xyxy))

        count_img_strings = []
        for img in count_results.ims:
            bytes_io = io.BytesIO()
            img_base64 = Image.fromarray(img)
            img_base64.save(bytes_io, format="jpeg")
            img_string = base64.b64encode(bytes_io.getvalue())
            count_img_strings.append(img_string)

        congestion_img_strings = []
        for img in congestion_results.ims:
            bytes_io = io.BytesIO()
            img_base64 = Image.fromarray(img)
            img_base64.save(bytes_io, format="jpeg")
            img_string = base64.b64encode(bytes_io.getvalue())
            congestion_img_strings.append(img_string)

        output_payload = {"camera_id": camera_ids, "images_datetime": images_datetime, "count": count_vehicles, "congestion": congestions,
                          "count_img_strings": count_img_strings, "congestion_img_strings": congestion_img_strings}

        return output_payload  # uvicorn main:app --reload --host 0.0.0.0 --port 8000


'''
CALLBACKS
'''


def callback87(channel, method, properties, body):
    print(" [x] callback87 Received") 
    # print(" [x] Received %r" % body) #called alr
    try:
        output_payload = get_predictions(body)

        message = json.dumps(output_payload)
        channel.basic_publish(
            exchange="", routing_key="ModelFileQ", body=message)

        channel.basic_ack(delivery_tag = method.delivery_tag)
        
        print(" [x] Sent prediction87S json to RabbitMQ")

    except Exception as e:
        print("failed to send message")
        print(str(e))


def callbackONE(channel, method, properties, body):
    # print(" [x] Received %r" % body)
    print(" [x] Received %r")
    try:
        '''
        ASSUME BODY in bytes is serialised byte
        '''
        output_payload = get_prediction(body)

        message = json.dumps(output_payload)
        channel.basic_publish(
            exchange="", routing_key="ModelInterfaceQ", body=message)

        channel.basic_ack(delivery_tag = method.delivery_tag)
        print(" [x] Sent predictionONE json to RabbitMQ")

    except Exception as e:
        print("failed to send message")
        print(str(e))



if __name__ == "__main__":
    while True:
        try:
            print(1)
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            print(2)
            channel = connection.channel()
            break
        
        except Exception as e:
            print("Waiting for connection")
            time.sleep(5)

    channel.queue_declare(queue='ApiModelQ')
    channel.queue_declare(queue='InterfaceModelQ')
    channel.queue_declare(queue='ModelInterfaceQ')
    channel.queue_declare(queue='ModelFileQ')

    print(3)
    channel.basic_consume(on_message_callback = callback87, queue='ApiModelQ', auto_ack=True)
    channel.basic_consume(on_message_callback = callbackONE, queue='InterfaceModelQ', auto_ack=True)

    print(4)
    channel.start_consuming()
    print(5)

# def on_open(connection):
#     connection.channel(on_open_callback=on_channel_open)

# def on_channel_open(channel):
#     channel.queue_declare(queue='ApiModelQ')
#     channel.queue_declare(queue='InterfaceModelQ')
#     channel.queue_declare(queue='ModelInterfaceQ')
#     channel.queue_declare(queue='ModelFileQ')

#     channel.basic_consume(on_message_callback = callback87, queue='ApiModelQ', auto_ack=True)
#     channel.basic_consume(on_message_callback = callbackONE, queue='InterfaceModelQ', auto_ack=True)

#     # channel.start_consuming()


# if __name__ == "__main__":
#     count_model = get_count_model()
#     congestion_model = get_congestion_model()

#     print("ola")
    
#     while True:
#         try:
#             print(0)
#             credentials = pika.PlainCredentials("guest", "guest")
#             print("1")
#             connection = pika.BlockingConnection(
#                 pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000), #added hearbeat
#                 on_open_callback = on_open
#             )
#             print("2")
#             # channel = connection.channel()
#             break
        
#         except Exception as e:
#             print("Waiting for connection")
#             time.sleep(5)

#     try:
#         connection.ioloop.start()
#     except KeyboardInterrupt:
#         connection.close()

    