import socket
import json
import pika

# ⚙️ Konfiguracja serwera TCP
TCP_IP = '0.0.0.0'
TCP_PORT = 9000
BUFFER_SIZE = 4096

# ⚙️ Konfiguracja RabbitMQ
RABBIT_HOST = 'localhost'
RABBIT_QUEUE = 'tcp_input'

# Połączenie z RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
channel = connection.channel()
channel.queue_declare(queue=RABBIT_QUEUE, durable=True)
print(f"✅ Połączono z RabbitMQ, kolejka: {RABBIT_QUEUE}")

# Funkcja obsługi klienta TCP
def handle_client(conn, addr):
    try:
        print(f"📥 Połączono z: {addr}")
        data = conn.recv(BUFFER_SIZE)
        if not data:
            conn.close()
            return

        # 🔹 Odczyt JSON z TCP
        tcp_data = json.loads(data.decode("utf-8"))
        print(f"📦 Odebrano dane TCP: {tcp_data}")

        # 🔹 Wysłanie danych do RabbitMQ
        channel.basic_publish(
            exchange='',
            routing_key=RABBIT_QUEUE,
            body=json.dumps(tcp_data),
            properties=pika.BasicProperties(
                delivery_mode=2  # wiadomość trwała
            )
        )
        print(f"➡️ Wysłano do RabbitMQ: {tcp_data}")

        # 🔹 Odpowiedź do klienta TCP
        ack_msg = {"status": "ok", "msg": "Dane wysłane do RabbitMQ"}
        conn.send(json.dumps(ack_msg).encode("utf-8"))

    except Exception as e:
        error_msg = {"error": str(e)}
        conn.send(json.dumps(error_msg).encode("utf-8"))
    finally:
        conn.close()
        print(f"❌ Rozłączono z: {addr}")

# Start serwera TCP
def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TCP_IP, TCP_PORT))
    server_socket.listen(5)
    print(f"🚀 Serwer TCP uruchomiony na {TCP_IP}:{TCP_PORT}")

    while True:
        conn, addr = server_socket.accept()
        handle_client(conn, addr)

if __name__ == "__main__":
    start_tcp_server()