from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

"""
This module sets up the SQLAlchemy database engine and session factory,
and provides a dependency function for FastAPI to inject database sessions.
"""

engine = create_engine(
    settings.database_url.replace("postgres://", "postgresql://", 1),
    echo=False,          
    future=True        
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)

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
