from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

"""
This module sets up the SQLAlchemy database engine and session factory,
and provides a dependency function for FastAPI to inject database sessions.
"""

# Create the SQLAlchemy engine using our DATABASE_URL
engine = create_engine(
    settings.database_url,
    echo=True,            # logs all SQL for debugging
    future=True           # use SQLAlchemy 2.0 style
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)

# Dependency function for FastAPI to get a DB session per request
def get_db():
    """
    FastAPI dependency that yields a database session for each request.

    Yields:
        Session: SQLAlchemy session object tied to the request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
