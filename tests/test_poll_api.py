import pytest
from app.schemas.poll_job import PollJobResponse

def test_create_poll_job(client):
    """
    Test the /prices/poll endpoint to ensure a poll job is created
    and the response matches expected schema and values.
    """
    body = {"symbols": ["AAPL","MSFT"], "interval": 30, "provider": "finnhub"}
    resp = client.post("/prices/poll", json=body)
    assert resp.status_code == 202

    data = resp.json()
    parsed = PollJobResponse(**data)
    assert parsed.config.symbols == ["AAPL","MSFT"]
    assert parsed.config.interval == 30
    assert parsed.status == "accepted"
    assert parsed.job_id
