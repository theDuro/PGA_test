print("rabbitmq.py LOADED")

import os
import json
import threading
from queue import Queue
import pika

# =========================
# KONFIGURACJA
# =========================
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

OUTPUT_QUEUE_NAME = os.getenv("OUTPUT_QUEUE_NAME", "output")       # tutaj wysyłamy
DB_INPUT_QUEUE_NAME = os.getenv("DB_INPUT_QUEUE_NAME", "db_input")  # tutaj nasłuch

# =========================
# KOLEJKA DLA SSE
# =========================
sse_queue: Queue = Queue()

# =========================
# PRODUCER (OUTPUT)
# =========================
def send_to_output(data: dict):
    """
    Wysyła wiadomość na kolejkę 'output'
    """
    print(f"send_to_output -> {OUTPUT_QUEUE_NAME}")

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

    channel.basic_publish(
        exchange="",
        routing_key=OUTPUT_QUEUE_NAME,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()

# =========================
# CONSUMER (DB_INPUT)
# =========================
def _consume_db_input():
    """
    Konsument nasłuchuje na kolejce 'db_input'
    """
    print(f"RabbitMQ CONSUMER listening on '{DB_INPUT_QUEUE_NAME}'")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=DB_INPUT_QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        message = body.decode()
        print(f"DB_INPUT RECEIVED: {message}")
        sse_queue.put(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=DB_INPUT_QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False,
    )

    channel.start_consuming()

def start_db_input_consumer():
    thread = threading.Thread(target=_consume_db_input, daemon=True)
    thread.start()

# =========================
# URUCHOMIENIE
# =========================
start_db_input_consumer()