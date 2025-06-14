import json
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

from datetime import datetime
from confluent_kafka import Consumer
from sqlalchemy.orm import Session
from ..core.dependencies import engine, SessionLocal
from ..models.raw_response import RawResponse
from ..models.symbol_average import SymbolAverage


def calculate_moving_average(prices):
    """
    Calculate the simple average of the last N prices.

    Args:
        prices (List[float]): A list of recent price values.

    Returns:
        float: The computed moving average.
    """
    return sum(prices) / len(prices)

def run_consumer():
    """
    Kafka consumer that listens to 'price-events', computes
    5-point moving averages, and updates the SymbolAverage table.
    """
    consumer = Consumer({
        "bootstrap.servers": "127.0.0.1:9092",
        "group.id": "ma_consumer_group",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe(["price-events"])

    db: Session = SessionLocal()
    try:
        logger.info("Starting MA consumer…")
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.debug("Kafka error:", msg.error())
                continue

            raw = msg.value()
            if not raw:
                continue

            try:
                event = json.loads(raw.decode("utf-8"))
            except ValueError:
                logger.debug("Skipping non-JSON message:", raw)
                continue

            symbol = event.get("symbol")
            if not symbol:
                continue

            rows = (
                db.query(RawResponse.price).filter(RawResponse.symbol == symbol).order_by(RawResponse.timestamp.desc()).limit(5).all()
            )
            prices = [r[0] for r in rows]
            if len(prices) < 5:
                continue

            ma = calculate_moving_average(prices)

            avg_row = (
                db.query(SymbolAverage).filter(SymbolAverage.symbol == symbol, SymbolAverage.window == "5").one_or_none()
            )
            if avg_row:
                avg_row.average   = ma
                avg_row.timestamp = datetime.utcnow()
            else:
                avg_row = SymbolAverage(symbol=symbol, average=ma, window="5", timestamp=datetime.utcnow())
                db.add(avg_row)

            db.commit()
            logger.info(f"[{datetime.utcnow()}] {symbol} 5-point MA = {ma:.2f}")

    finally:
        db.close()
        consumer.close()

if __name__ == "__main__":
    run_consumer()
