import pika
import json
import os

print("rabbitmq.py LOADED")  # DEBUG

# Pobranie konfiguracji RabbitMQ z zmiennych środowiskowych lub wartości domyślnych
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")
QUEUE_NAME = os.getenv("QUEUE_NAME", "ml_input")


def send_to_rabbitmq(data: dict):
    """
    Wysyła dane (słownik) do kolejki RabbitMQ w formacie JSON.
    """
    print(f"send_to_rabbitmq CALLED - connecting to {RABBITMQ_HOST}:{RABBITMQ_PORT}")

    # Tworzymy połączenie z RabbitMQ z uwierzytelnieniem
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()

    # Deklaracja kolejki (jeśli nie istnieje) z opcją durable
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    print(f"Queue '{QUEUE_NAME}' declared or already exists.")

    # Wysyłanie danych jako JSON
    message = json.dumps(data)
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),  # trwałe wiadomości
    )
    print(f"Message sent to queue '{QUEUE_NAME}': {message}")

    # Zamknięcie połączenia
    connection.close()
    print("Connection closed.")
    

# Przykład testowy (uruchomienie modułu samodzielnie)
if __name__ == "__main__":
    sample_data = {"test": "Hello RabbitMQ!"}
    send_to_rabbitmq(sample_data)
