from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import ProductionData
from rabbitmq import send_to_rabbitmq

import pika
import json
import threading
import queue

app = FastAPI(title="Metal Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🟢 Tu trzymamy dane, które RabbitMQ wyśle do frontendu
sse_queue = queue.Queue()

@app.post("/data")
def receive_production_data(data: ProductionData):
    payload = data.dict()
    print("Received production data:", payload)
    send_to_rabbitmq(payload)
    return {"status": "ok", "message": "Production data sent to RabbitMQ", "data": payload}

# SSE endpoint
@app.get("/stream")
def stream():
    def event_generator():
        while True:
            data = sse_queue.get()  # blokuje do momentu, gdy coś pojawi się w kolejce
            yield f"data: {json.dumps(data)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 🟢 Funkcja nasłuchująca RabbitMQ i wrzucająca dane do sse_queue
def rabbitmq_listener():
    RABBITMQ_HOST = "localhost"
    QUEUE_NAME = "sensor_data"

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        sse_queue.put(data)  # wrzucamy dane do kolejki SSE
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("RabbitMQ listener started...")
    channel.start_consuming()

# Uruchamiamy listener w osobnym wątku
threading.Thread(target=rabbitmq_listener, daemon=True).start()
