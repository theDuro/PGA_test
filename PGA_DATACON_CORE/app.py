from fastapi import FastAPI
from models import ProductionData
from rabbitmq import send_to_rabbitmq
from fastapi.middleware.cors import CORSMiddleware  # <- nie instalujesz nic!

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