import uuid
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SymbolAverage(Base):
    """
    SQLAlchemy model for storing moving average values of market symbols.

    Each record represents the computed average over a fixed window (e.g., 5-point)
    at a specific timestamp for a given symbol.
    """
    __tablename__ = "symbol_averages"

    id        = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol    = Column(String, index=True, nullable=False)
    average   = Column(Float, nullable=False)
    window    = Column(String, nullable=False, default="5")  # e.g. “5-point”
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
