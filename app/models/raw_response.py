# app/models/raw_response.py

import uuid
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Base class for all ORM models
Base = declarative_base()

class RawResponse(Base):

    """
    Base = declarative_base() sets up SQLAlchemy's ORM base class.
    Each Column maps to a table column.
    We index on symbol and timestamp to speed up queries.
    raw_json stores the full API response for auditing or replay.
    """

    __tablename__ = "raw_market_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    provider = Column(String, nullable=False)
    raw_json = Column(String, nullable=False)
