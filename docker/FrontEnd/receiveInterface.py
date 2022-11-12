import pika
import time
import pandas as pd
import ast

def callbackInterfaceClient(channel, method, properties, body):
    # Sends image
    if properties.headers.get("key") == "ImagePrediction":
        # process json string (body) to json
        # json_file change to dataframe (now u hv the prediction jam and count)
        # output saved to a csv in FrontEnd with name ImagePrediction.csv
        pd.DataFrame(ast.literal_eval(body)).to_csv('ImagePrediction.csv',index=False)

    # Sends incidents request
    elif properties.headers.get("key") == "Incidents":
        # process json string (body) to json
        # json_file to dataframe (if needed)
        # output saved to a csv in FrontEnd with name Incidents.csv
        pd.DataFrame(ast.literal_eval(body)).to_csv('Incidents.csv',index=False)

    # Sends ltaDump request
    elif properties.headers.get("key") == "Ltadump":
        # first try: to read the Ltadump.csv 
        # error
        #process json string
        #etc
        # output saved to a csv in FrontEnd with name Ltadump.csv
        #  if theres no error then we append 
        while True:
            try:
                pd.read_csv('Ltadump.csv')
            except:
                time.sleep(5)
            else:
                old=pd.read_csv('Ltadump.csv')
                new=pd.DataFrame(ast.literal_eval(body))
                pd.concat([old,new]).to_csv('Ltadump.csv')
                break

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