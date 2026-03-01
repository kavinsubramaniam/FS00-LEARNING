from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer
import json
import uuid
from datetime import datetime, timezone

class OrderRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int
    price: float

app = FastAPI()
producer = Producer({'bootstrap.servers': 'localhost:9092'})
KAFKA_TOPIC = 'orders'

def delivery_report(err, msg):
    if err is not None:
        print("❌ Delivery failed:", err)
    else:
        print(
            f"✅ Delivered to topic={msg.topic()} partition={msg.partition()} offset={msg.offset()}"
        )

@app.post("/order")
def create_order(order: OrderRequest):
    try:
        order_event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "ORDER_CREATED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": order.model_dump(),
        }

        producer.produce(
            topic=KAFKA_TOPIC,
            value=json.dumps(order_event).encode("utf-8"),
            on_delivery=delivery_report,
        )

        # Important: allow background delivery callbacks to run
        producer.poll(0)

        return {"status": "success", "event": order_event}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)