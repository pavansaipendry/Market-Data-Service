import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient instance for testing HTTP endpoints.
    """
    return TestClient(app)
