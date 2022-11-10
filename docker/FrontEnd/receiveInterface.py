import pika
import time

def callbackInterfaceClient(channel, method, properties, body):
    # Sends image
    if properties.headers.get("key") == "ImagePrediction":
        # process json string (body) to json
        # json_file change to dataframe (now u hv the prediction jam and count)
        # output saved to a csv in FrontEnd with name ImagePrediction.csv


    # Sends incidents request
    elif properties.headers.get("key") == "Incidents":
        # process json string (body) to json
        # json_file to dataframe (if needed)
        # output saved to a csv in FrontEnd with name Incidents.csv

    # Sends ltaDump request
    elif properties.headers.get("key") == "Ltadump":
        # first try: to read the Ltadump.csv 
        # whatever df we read ['timestamp']=time.now()
        # error
        #process json string
        #etc
        # output saved to a csv in FrontEnd with name Ltadump.csv
        #  if theres no error then we append 

if __name__ == "__main__":
    # Connects ApiServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("ApiServer waiting for connection")
            time.sleep(5)

    channel.queue_declare(queue='InterfaceClientQ')
    channel.basic_consume(queue='InterfaceClientQ', on_message_callback = callbackInterfaceClient, auto_ack=True)


    channel.start_consuming()