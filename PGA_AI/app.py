import json
import numpy as np
import pika
import joblib

# 1️⃣ Wczytaj wytrenowany model
model = joblib.load("model.joblib")
print("Model załadowany")

# 2️⃣ Połącz się z RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="rabbitmq")  # host RabbitMQ (w Docker Compose 'rabbitmq')
)
channel = connection.channel()

# 3️⃣ Utwórz kolejki (jeśli nie istnieją)
channel.queue_declare(queue="ml_input")
channel.queue_declare(queue="ml_output")

print("Czekam na dane z RabbitMQ...")

# 4️⃣ Funkcja obsługi wiadomości
def callback(ch, method, properties, body):
    try:
        # Odbiór danych
        data = json.loads(body)
        x = np.array(data["input"], dtype=np.float32).reshape(1, 6)

        # Predykcja modelu
        y = model.predict(x)[0].tolist()

        # Wysyłka wyniku do kolejki wyjściowej
        channel.basic_publish(
            exchange="",
            routing_key="ml_output",
            body=json.dumps({"output": y})
        )

        print("IN :", data["input"])
        print("OUT:", y)

        # Potwierdzenie obsługi wiadomości
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("BŁĄD:", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# 5️⃣ Konsumowanie wiadomości
channel.basic_consume(
    queue="ml_input",
    on_message_callback=callback
)

# 6️⃣ Start nasłuchiwania
channel.start_consuming()
