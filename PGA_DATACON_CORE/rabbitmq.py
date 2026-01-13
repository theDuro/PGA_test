import json
import numpy as np
import pika
import joblib
import time
import os
from queue import Queue
from threading import Thread

# Queue dla SSE – FastAPI będzie ją czytać
sse_queue = Queue()

# Konfiguracja RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")
QUEUE_INPUT = os.getenv("QUEUE_INPUT", "ml_input")
QUEUE_OUTPUT = os.getenv("QUEUE_OUTPUT", "output")

# Funkcja wysyłania danych do RabbitMQ (używana przez FastAPI)
def send_to_rabbitmq(data: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_INPUT, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_INPUT,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    print(f"✅ Wysłano do '{QUEUE_INPUT}': {data}")

# Retry połączenia do RabbitMQ
def connect_rabbitmq(max_retries=10):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
            )
            print(f"✅ Połączono z RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            return connection
        except Exception as e:
            print(f"❌ Próba {i+1}/{max_retries} - Błąd połączenia: {e}")
            time.sleep(5)
    raise Exception("Nie udało się połączyć z RabbitMQ")

# Wczytaj model ML
model = joblib.load("model.joblib")
print("✅ Model ML załadowany")

# Callback obsługi wiadomości
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"📥 Odebrano: {data}")

        x = np.array(data["input"], dtype=np.float32).reshape(1, -1)
        y = model.predict(x)[0].tolist()

        result = {
            "input": data["input"],
            "output": y,
            "timestamp": data.get("timestamp", "")
        }

        # Publikacja do output queue
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_OUTPUT,
            body=json.dumps(result),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Dodaj do SSE queue
        sse_queue.put(json.dumps(result))

        print(f"✅ Predykcja: IN={data['input']} → OUT={y}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"❌ BŁĄD: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# Funkcja do startu consumer RabbitMQ w osobnym wątku
def start_rabbitmq_consumer():
    global channel
    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_INPUT, durable=True)
    channel.queue_declare(queue=QUEUE_OUTPUT, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_INPUT, on_message_callback=callback)
    print("🚀 RabbitMQ consumer uruchomiony!")
    channel.start_consuming()

# Uruchom w osobnym wątku
thread = Thread(target=start_rabbitmq_consumer, daemon=True)
thread.start()