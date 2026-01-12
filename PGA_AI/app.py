import socket
import json
import pika
import os
import time

# Konfiguracja
TCP_IP = '0.0.0.0'
TCP_PORT = int(os.getenv("TCP_PORT", 9000))
BUFFER_SIZE = 4096

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBIT_QUEUE = 'tcp_input'

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
            print(f"❌ Próba {i+1}/{max_retries} - Błąd: {e}")
            time.sleep(5)
    raise Exception("Nie udało się połączyć z RabbitMQ")

# Połączenie z RabbitMQ
connection = connect_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue=RABBIT_QUEUE, durable=True)
print(f"✅ Kolejka '{RABBIT_QUEUE}' gotowa")

# Obsługa klienta TCP
def handle_client(conn, addr):
    try:
        print(f"📥 Połączono z: {addr}")
        data = conn.recv(BUFFER_SIZE)
        
        if not data:
            conn.close()
            return
        
        # Dekodowanie JSON z TCP
        tcp_data = json.loads(data.decode("utf-8"))
        print(f"📦 Odebrano TCP: {tcp_data}")
        
        # Wysłanie do RabbitMQ
        channel.basic_publish(
            exchange='',
            routing_key=RABBIT_QUEUE,
            body=json.dumps(tcp_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"✅ Wysłano do RabbitMQ: {tcp_data}")
        
        # Odpowiedź ACK
        ack = {"status": "ok", "message": "Data received"}
        conn.send(json.dumps(ack).encode("utf-8"))
        
    except json.JSONDecodeError as e:
        error = {"error": "Invalid JSON", "details": str(e)}
        conn.send(json.dumps(error).encode("utf-8"))
        print(f"❌ Błąd JSON: {e}")
        
    except Exception as e:
        error = {"error": str(e)}
        conn.send(json.dumps(error).encode("utf-8"))
        print(f"❌ Błąd: {e}")
        
    finally:
        conn.close()
        print(f"❌ Rozłączono: {addr}")

# Start serwera TCP
def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_IP, TCP_PORT))
    server.listen(5)
    print(f"🚀 Serwer TCP uruchomiony: {TCP_IP}:{TCP_PORT}")
    
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)

if __name__ == "__main__":
    start_tcp_server()