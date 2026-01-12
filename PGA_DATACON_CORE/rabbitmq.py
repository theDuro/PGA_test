import pika
import json
import os

print("rabbitmq.py LOADED")  # DEBUG

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "sensor_data"


def send_to_rabbitmq(data: dict):
    print("send_to_rabbitmq CALLED")  # DEBUG

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()