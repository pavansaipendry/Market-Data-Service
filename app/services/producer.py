import json
from confluent_kafka import Producer
from ..core.config import settings

producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})

def publish_price_event(event: dict):
    producer.produce("price-events", json.dumps(event).encode())
    producer.flush()