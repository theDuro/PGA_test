import socket
import json
import pika
import os
import time

# Konfiguracja TCP
TCP_IP = '0.0.0.0'
TCP_PORT = int(os.getenv("TCP_PORT", 9000)) ## todo plc tcp port lower >5000 !!!
BUFFER_SIZE = 4096

# Konfiguracja RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_OUTPUT_QUEUE = 'output'  # Kolejka docelowa dla SSE / FastAPI

# Retry connection do RabbitMQ
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
            print(f"✅ Połączono z RabbitMQ: {RABBITMQ_HOST}")
            return connection
        except Exception as e:
            print(f"❌ Próba {i+1}/{max_retries} - Błąd połączenia: {e}")
            time.sleep(5)
    raise Exception("Nie udało się połączyć z RabbitMQ")

# Połączenie z RabbitMQ
connection = connect_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue=RABBIT_OUTPUT_QUEUE, durable=True)
print(f"✅ Kolejka '{RABBIT_OUTPUT_QUEUE}' gotowa")

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
        
        # Wysłanie do kolejki 'output'
        channel.basic_publish(
            exchange='',
            routing_key=RABBIT_OUTPUT_QUEUE,
            body=json.dumps(tcp_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"✅ Wysłano do RabbitMQ '{RABBIT_OUTPUT_QUEUE}': {tcp_data}")
        
        # Odpowiedź ACK do klienta TCP
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