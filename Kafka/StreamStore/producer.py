from confluent_kafka import Producer
import json
import uuid

producer_config = {
    "bootstrap.servers":"localhost:9092"
}

producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

order = {
    "order_id": str(uuid.uuid4()),
    "customer_id": str(uuid.uuid4()),
    "item": "Sample Item",
    "total_price": 29.99
}

producer.produce(
    "orders", 
    key=order["order_id"], 
    value=json.dumps(order), 
    callback=delivery_report
)
producer.flush()