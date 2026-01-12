FROM python:3.11-slim

WORKDIR /app

# Instalacja pika (RabbitMQ client)
RUN pip install --no-cache-dir pika

# Kopiowanie skryptu
COPY tcp_to_rabbit.py .

# Ekspozycja portu TCP
EXPOSE 9000

CMD ["python", "-u", "tcp_to_rabbit.py"]