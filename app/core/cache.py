import redis
import json
from .config import settings

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

logger.debug(f"[cache] Connecting to Redis @ {settings.redis_host}:{settings.redis_port}, db=0")

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,
)

def make_cache_key(symbol: str, provider: str) -> str:
    """
    Generate a standardized Redis cache key for a given symbol and data provider.

    Args:
        symbol (str): The market symbol (e.g., "AAPL").
        provider (str): The data provider name (e.g., "finnhub").

    Returns:
        str: A Redis key in the format "price:SYMBOL:provider"
    """
    key = f"price:{symbol.upper()}:{provider}"
    logger.info(f"[cache] Generated cache key: {key}")
    return key
