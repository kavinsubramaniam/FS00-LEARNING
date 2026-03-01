import json
from confluent_kafka import Consumer


BOOTSTRAP = "localhost:9092"
TOPIC = "orders"
GROUP_ID = "notification-service"


def main():
    consumer = Consumer(
        {
            "bootstrap.servers": BOOTSTRAP,
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )

    consumer.subscribe([TOPIC])
    print(f"📩 Notification Service listening on topic: {TOPIC}")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print("❌ Kafka error:", msg.error())
                continue

            event = json.loads(msg.value().decode("utf-8"))

            if event.get("event_type") == "ORDER_CREATED":
                data = event["data"]
                print(
                    f"✅ Notify user={data['user_id']} "
                    f"order for product={data['product_id']} qty={data['quantity']}"
                )
            else:
                print("⚠️ Unknown event:", event)

    except KeyboardInterrupt:
        print("Stopping consumer...")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()
