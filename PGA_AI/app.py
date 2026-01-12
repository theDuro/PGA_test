import json
import numpy as np
import pika
import joblib
import time
import os

# Wczytaj host RabbitMQ z env
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# Retry connection do RabbitMQ
def connect_rabbitmq(max_retries=10):
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            print(f"✅ Połączono z RabbitMQ: {RABBITMQ_HOST}")
            return connection
        except Exception as e:
            print(f"❌ Próba {i+1}/{max_retries} - Błąd połączenia: {e}")
            time.sleep(5)
    raise Exception("Nie udało się połączyć z RabbitMQ")

# Wczytaj model
model = joblib.load("model.joblib")
print("✅ Model ML załadowany")

# Połącz z RabbitMQ
connection = connect_rabbitmq()
channel = connection.channel()

# Deklaracja kolejek
channel.queue_declare(queue="ml_input", durable=True)
channel.queue_declare(queue="ml_output", durable=True)

print("🔄 Czekam na dane z kolejki 'ml_input'...")

# Callback obsługi wiadomości
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"📥 Odebrano: {data}")
        
        # Przygotowanie danych do predykcji
        x = np.array(data["input"], dtype=np.float32).reshape(1, -1)
        
        # Predykcja
        y = model.predict(x)[0].tolist()
        
        # Wysłanie wyniku
        result = {
            "input": data["input"],
            "output": y,
            "timestamp": data.get("timestamp", "")
        }
        
        channel.basic_publish(
            exchange="",
            routing_key="ml_output",
            body=json.dumps(result),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        print(f"✅ Predykcja: IN={data['input']} → OUT={y}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"❌ BŁĄD: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# Konsumuj wiadomości
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="ml_input", on_message_callback=callback)

# Start
print("🚀 AI Service uruchomiony!")
channel.start_consuming()