from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import ProductionData
from rabbitmq import send_to_rabbitmq, sse_queue  # sse_queue to Queue z rabbitmq.py
import asyncio

app = FastAPI(title="Metal Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/data")
def receive_production_data(data: ProductionData):
    payload = data.dict()
    print("Received production data:", payload)
    send_to_rabbitmq(payload)
    return {
        "status": "ok",
        "message": "Production data sent to RabbitMQ",
        "data": payload
    }

@app.get("/events")
async def sse_events():
    """
    Endpoint SSE – streamuje wszystkie JSONy z kolejki sse_queue.
    """
    async def event_generator():
        while True:
            data = await asyncio.to_thread(sse_queue.get)
            yield f"data: {data}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")