import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.cache import redis_client, make_cache_key
from ..schemas.price import PriceResponse
from ..schemas.poll_job import PollJobCreate, PollJobResponse, PollJobConfig
from ..services.provider import FinnhubProvider
from ..services.producer import publish_price_event
from ..core.dependencies import get_db
from ..models.raw_response import RawResponse
from ..models.poll_job import PollJob
from ..services.scheduler import add_poll_job

router = APIRouter(prefix="/prices", tags=["prices"])
finnhub_provider = FinnhubProvider()

@router.get("/latest", response_model=PriceResponse)
def get_latest_price(
    symbol: str,
    provider: Optional[str] = Query(
        None,
        description="Data provider (e.g. finnhub, alpha_vantage). Defaults to finnhub if omitted."
    ),
    db: Session = Depends(get_db),
):
    info = redis_client.info()
    logger.debug("Redis INFO run_id=%s tcp_port=%s", info.get('run_id'), info.get('tcp_port'))

    conn = redis_client.connection_pool.connection_kwargs
    logger.debug("Redis in use: host=%s port=%s db=%s", conn.get('host'), conn.get('port'), conn.get('db'))

    source = provider or "finnhub"
    cache_key = make_cache_key(symbol, source)
    logger.debug("Looking up cache key: %s", cache_key)

    cached = redis_client.get(cache_key)
    if cached:
        logger.info("Cache HIT for key: %s", cache_key)
        data = json.loads(cached)         
    else:
        logger.info("Cache MISS for key: %s, fetching from provider...", cache_key)
        try:
            data = finnhub_provider.get_latest_price(symbol)
            data["provider"] = source

            if not isinstance(data["timestamp"], datetime):
                try:
                    data["timestamp"] = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logger.error("Timestamp parse error: %s", e)
                    raise HTTPException(status_code=500, detail="Timestamp format not recognized.")

            dt: datetime = data["timestamp"]
            data["timestamp"] = dt.isoformat() + "Z"

        except Exception as e:
            logger.error("Error fetching from Finnhub: %s", e)
            raise HTTPException(status_code=502, detail="Error fetching from Finnhub")

    raw = RawResponse(
        symbol    = data["symbol"],
        price     = data["price"],
        timestamp = data["timestamp"],
        provider  = data["provider"],
        raw_json  = json.dumps(data.get("raw", {})),
    )
    db.add(raw)
    db.commit()

    logger.debug("Persisted raw response with timestamp: %s", data["timestamp"])

    publish_price_event({
        "symbol":          data["symbol"],
        "price":           data["price"],
        "timestamp":       data["timestamp"],
        "source":          data["provider"],
        "raw_response_id": raw.id,
    })

    logger.debug("Setting cache key: %s", cache_key)
    redis_client.set(cache_key, json.dumps(data), ex=30)
    logger.info("Cache SET complete for key: %s", cache_key)

    return data


@router.post(
    "/poll",
    response_model=PollJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_poll_job(
    req: PollJobCreate,
    db: Session = Depends(get_db),
):
    """
    Schedule a polling job:
    - persists the symbols, interval, provider
    - returns a job_id + accepted status + config
    """

    job = PollJob(
        symbols   = req.symbols,
        interval  = req.interval,
        provider  = req.provider,
        status    = "accepted",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    add_poll_job(job.id, job.interval)

    return PollJobResponse(
        job_id = job.id,
        status = job.status,
        config = PollJobConfig(
            symbols  = job.symbols,
            interval = job.interval,
        ),
    )