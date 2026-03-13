from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rabbitmq import send_to_rabbitmq, sse_queue
import asyncio

app = FastAPI(title="Metal Production API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint przyjmujący dowolny JSON
@app.post("/data")
async def receive_production_data(request: Request):
    payload = await request.json()
    print("Received production data:", payload)
    send_to_rabbitmq(payload)
    return {
        "status": "ok",
        "message": "Data sent to RabbitMQ",
        "data": payload
    }


@app.get("/stream")
async def sse_events():
    async def event_generator():
        while True:
            try:
                # Nieblokujące sprawdzenie kolejki
                data = sse_queue.get_nowait()
                yield f"data: {data}\n\n"
            except Exception:
                # Kolejka pusta — keepalive i czekaj
                yield ": keepalive\n\n"
                await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )