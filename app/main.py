import uvicorn
import logging
from fastapi import FastAPI
from sqlalchemy.orm import Session
from .api.prices import router
from .models.raw_response import Base as RawBase
from .models.symbol_average import Base as AvgBase
from .models.poll_job import Base as PollJobBase, PollJob
from .core.dependencies import engine, SessionLocal
from .services.scheduler import start_scheduler, add_poll_job

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
)

app = FastAPI(title="Market Data Service")
app.include_router(router)

@app.on_event("startup")

def on_startup():
    """
    App startup hook:
    - Creates all DB tables.
    - Starts APScheduler.
    - Re-schedules previously accepted poll jobs.
    """

    RawBase.metadata.create_all(bind=engine)
    AvgBase.metadata.create_all(bind=engine)
    PollJobBase.metadata.create_all(bind=engine)

    start_scheduler()

    db: Session = SessionLocal()
    try:
        active_jobs = db.query(PollJob).filter(PollJob.status == "accepted").all()
        for job in active_jobs:
            add_poll_job(job.id, job.interval)
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
