import json
import pika

def callback(ch, method, properties, body):
    data = json.loads(body)
    print("WYNIK:", data["output"])
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="rabbitmq")
)
channel = connection.channel()

channel.queue_declare(queue="ml_output")

channel.basic_consume(
    queue="ml_output",
    on_message_callback=callback
)

print("Czekam na wyniki...")
channel.start_consuming()
