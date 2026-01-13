import json
import numpy as np
import pika
import joblib
import time
import os

# -----------------------------
# Konfiguracja RabbitMQ
# -----------------------------
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

QUEUE_INPUT = os.getenv("QUEUE_INPUT", "ml_input")
QUEUE_OUTPUT = os.getenv("QUEUE_OUTPUT", "output")

# -----------------------------
# Funkcja łączenia z RabbitMQ z retry
# -----------------------------
def connect_rabbitmq(max_retries=10):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            print(f"✅ Połączono z RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            return connection
        except Exception as e:
            print(f"❌ Próba {i+1}/{max_retries} - Błąd połączenia: {e}")
            time.sleep(5)
    raise Exception("Nie udało się połączyć z RabbitMQ")

# -----------------------------
# Wczytanie modelu ML
# -----------------------------
model = joblib.load("model.joblib")
print("✅ Model ML załadowany")

# -----------------------------
# Połączenie z RabbitMQ i deklaracja kolejek
# -----------------------------
connection = connect_rabbitmq()
channel = connection.channel()

# Deklaracja kolejek input/output
channel.queue_declare(queue=QUEUE_INPUT, durable=True)
channel.queue_declare(queue=QUEUE_OUTPUT, durable=True)

print(f"🔄 Czekam na dane w kolejce '{QUEUE_INPUT}'...")

# -----------------------------
# Funkcja callback - nasłuch input
# -----------------------------
def callback(ch, method, properties, body):
    try:
        # Zamiana JSON → dict
        data = json.loads(body)
        print(f"📥 Odebrano: {data}")
        
        # Przygotowanie danych dla modelu ML
        x = np.array(data["input"], dtype=np.float32).reshape(1, -1)
        
        # Predykcja
        y = model.predict(x)[0].tolist()
        
        # Przygotowanie wyniku
        result = {
            "input": data["input"],
            "output": y,
            "timestamp": data.get("timestamp", "")
        }
        
        # Wysłanie wyniku do kolejki ml_output
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_OUTPUT,
            body=json.dumps(result),
            properties=pika.BasicProperties(delivery_mode=2)  # trwałe wiadomości
        )
        
        print(f"✅ Predykcja: IN={data['input']} → OUT={y}")
        
        # Potwierdzenie przetworzenia wiadomości
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"❌ BŁĄD podczas przetwarzania: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# -----------------------------
# Nasłuchiwanie kolejki ml_input
# -----------------------------
channel.basic_qos(prefetch_count=1)  # jedna wiadomość naraz
channel.basic_consume(queue=QUEUE_INPUT, on_message_callback=callback)

# -----------------------------
# Start pętli nasłuchującej
# -----------------------------
print("🚀 AI Service uruchomiony!")
channel.start_consuming()
