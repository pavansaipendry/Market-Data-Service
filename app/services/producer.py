import json
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

# Kafka is optional: when KAFKA_BOOTSTRAP_SERVERS is unset (e.g. on the
# free-tier demo deployment) publishing becomes a no-op so the API still
# serves quotes from Finnhub + Postgres + Redis.
if settings.kafka_bootstrap_servers:
    from confluent_kafka import Producer
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
else:
    producer = None
    logger.info("Kafka disabled (no KAFKA_BOOTSTRAP_SERVERS) - price events not published")

def publish_price_event(event: dict):
    if producer is None:
        return
    producer.produce("price-events", json.dumps(event).encode())
    producer.flush()
