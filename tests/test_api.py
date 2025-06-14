import pytest
from datetime import datetime
from app.schemas.price import PriceResponse
from app.api.prices import finnhub_provider

# monkeypatch the FinnhubProvider so we don’t hit the real API
class DummyProvider:
    """
    Mock version of the FinnhubProvider to avoid hitting the real API during tests.
    """
    def get_latest_price(self, symbol: str):
        return {
            "symbol": symbol,
            "price": 123.45,
            "timestamp": datetime(2025, 1, 1, 12, 0, 0),
            "provider": "finnhub",
            "raw": {},
        }

@pytest.fixture(autouse=True)
def patch_provider(monkeypatch):
    """
    Automatically patch finnhub_provider.get_latest_price in all tests using DummyProvider.
    """
    monkeypatch.setattr(finnhub_provider, "get_latest_price", DummyProvider().get_latest_price)

def test_get_latest_price_ok(client):
    """
    Test the /prices/latest endpoint with mocked data to verify structure and correctness.
    """
    resp = client.get("/prices/latest?symbol=FOO")
    assert resp.status_code == 200

    data = resp.json()
    # Validate against the Pydantic schema
    parsed = PriceResponse(**data)
    assert parsed.symbol == "FOO"
    assert parsed.price == 123.45
    assert parsed.provider == "finnhub"
