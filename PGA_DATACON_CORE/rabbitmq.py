import pika
import json
import os
import threading
from queue import Queue

print("rabbitmq.py LOADED")

# =========================
# KONFIGURACJA
# =========================
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

INPUT_QUEUE_NAME = os.getenv("QUEUE_NAME", "ml_input")
OUTPUT_QUEUE_NAME = os.getenv("OUTPUT_QUEUE_NAME", "ml_output")

# =========================
# KOLEJKA DLA SSE
# =========================
sse_queue: Queue = Queue()

# =========================
# PRODUCER (INPUT)
# =========================
def send_to_rabbitmq(data: dict):
    print(f"send_to_rabbitmq -> {INPUT_QUEUE_NAME}")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=INPUT_QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=INPUT_QUEUE_NAME,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()

# =========================
# CONSUMER (OUTPUT)
# =========================
def _consume_output():
    print(f"RabbitMQ CONSUMER listening on '{OUTPUT_QUEUE_NAME}'")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=OUTPUT_QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        message = body.decode()
        print(f"OUTPUT RECEIVED: {message}")
        sse_queue.put(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=OUTPUT_QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False,
    )

    channel.start_consuming()

def start_output_consumer():
    thread = threading.Thread(target=_consume_output, daemon=True)
    thread.start()
