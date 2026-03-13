print("rabbitmq.py LOADED")

import os
import json
import time
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

INPUT_QUEUE_NAME = os.getenv("QUEUE_NAME", "ml_input")
OUTPUT_QUEUE_NAME = os.getenv("OUTPUT_QUEUE_NAME", "output")
DB_INPUT_QUEUE_NAME = os.getenv("DB_INPUT_QUEUE_NAME", "db_input")

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

# =========================
# KOLEJKA DLA SSE
# =========================
sse_queue: Queue = Queue()

# =========================
# SHARED CONNECTION HELPER
# =========================
def _make_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )
    )

# =========================
# PRODUCER (INPUT / DB)
# =========================
def send_to_rabbitmq(data: dict, queue_name=INPUT_QUEUE_NAME):
    """
    Wysyła wiadomość na dowolną kolejkę (domyślnie ml_input lub db_input).
    Ponawia próbę przy błędzie połączenia.
    """
    print(f"send_to_rabbitmq -> {queue_name}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            connection = _make_connection()
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            connection.close()
            return
        except pika.exceptions.AMQPConnectionError as e:
            print(f"send_to_rabbitmq: próba {attempt}/{MAX_RETRIES} nieudana: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    raise RuntimeError(f"Nie udało się wysłać wiadomości do kolejki '{queue_name}' po {MAX_RETRIES} próbach.")

# =========================
# CONSUMER (OUTPUT)
# =========================
def _consume_output():
    """
    Jeden konsument dla kolejki 'output'.
    Automatycznie wznawia połączenie po rozłączeniu.
    """
    print(f"RabbitMQ CONSUMER listening on '{OUTPUT_QUEUE_NAME}'")

    while True:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                connection = _make_connection()
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

                print(f"✅ Połączono z RabbitMQ (próba {attempt}), czekam na wiadomości...")
                channel.start_consuming()  # blocks here until connection drops

            except pika.exceptions.AMQPConnectionError as e:
                print(f"❌ Próba {attempt}/{MAX_RETRIES} - Błąd połączenia: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    print("❌ Przekroczono limit prób. Ponawiam całą pętlę za 30s...")
                    time.sleep(30)
                    break  # restart the outer while loop

            except Exception as e:
                # Unexpected error — log and reconnect
                print(f"❌ Nieoczekiwany błąd konsumenta: {e}")
                time.sleep(RETRY_DELAY)
                break  # restart the outer while loop

def start_output_consumer():
    thread = threading.Thread(target=_consume_output, daemon=True)
    thread.start()

# =========================
# URUCHOMIENIE
# =========================
start_output_consumer()