import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from ..core.dependencies import SessionLocal
from ..models.poll_job import PollJob
from ..services.provider import FinnhubProvider
from ..services.producer import publish_price_event
from ..models.raw_response import RawResponse
from ..core.cache import redis_client, make_cache_key

scheduler = BackgroundScheduler()
provider = FinnhubProvider()


def execute_poll(job_id: str):
    """
    Job function: fetch and publish latest prices for a given PollJob.
    """
    db: Session = SessionLocal()
    try:
        job = db.query(PollJob).filter(PollJob.id == job_id).one_or_none()
        if not job or job.status != "accepted":
            return
        
        job.status = "running"
        job.last_run_at = datetime.utcnow()
        db.commit()

        for symbol in job.symbols:
            data = provider.get_latest_price(symbol)
            raw = RawResponse(
                symbol    = data["symbol"],
                price     = data["price"],
                timestamp = data["timestamp"],
                provider  = data["provider"],
                raw_json  = json.dumps(data["raw"]),
            )
            db.add(raw)
            db.commit()

            publish_price_event({
                "symbol":          data["symbol"],
                "price":           data["price"],
                "timestamp":       data["timestamp"].isoformat() + "Z",
                "source":          data["provider"],
                "raw_response_id": raw.id,
            })

            cache_key = make_cache_key(data["symbol"], data["provider"])
            redis_client.set(
                cache_key,
                json.dumps(data),
                ex=job.interval 
            )

        next_run = datetime.utcnow() + timedelta(seconds=job.interval)
        job.next_run_at = next_run
        job.status = "accepted"
        db.commit()

    except Exception:
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """
    Start the APScheduler background service.
    """
    scheduler.start()


add_poll_job = lambda job_id, interval: scheduler.add_job(
    execute_poll,
    'interval',
    seconds=interval,
    id=job_id,
    args=[job_id],
    replace_existing=True,
)