from pydantic import BaseModel
from typing import List

class PollJobConfig(BaseModel):
    """
    Configuration details for a polling job.

    Includes the list of symbols to poll and the interval in seconds.
    """
    symbols: List[str]
    interval: int

class PollJobCreate(BaseModel):
    """
    Schema for creating a new polling job via API request.

    Includes symbols, interval, and provider information.
    """
    symbols: List[str]
    interval: int
    provider: str

class PollJobResponse(BaseModel):
    """
    Schema for API responses when a polling job is created.

    Returns a job ID, current status, and the job configuration.
    """
    job_id: str
    status: str
    config: PollJobConfig
