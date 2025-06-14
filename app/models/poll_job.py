import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PollJob(Base):
    """
    SQLAlchemy model representing a polling job.

    Stores job metadata including symbol list, provider, scheduling interval,
    and timestamps for job lifecycle tracking.
    """
    __tablename__ = "poll_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbols = Column(JSON, nullable=False)
    interval = Column(Integer, nullable=False)
    provider = Column(String, nullable=False, default="finnhub")
    status = Column(String, index=True, nullable=False, default="accepted")
    created_at  = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
