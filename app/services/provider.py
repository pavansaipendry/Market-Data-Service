import finnhub
from datetime import datetime
from ..core.config import settings

class FinnhubProvider:
    def __init__(self):
        self.client = finnhub.Client(api_key=settings.finnhub_api_key)

    def get_latest_price(self, symbol: str) -> dict:
        """
            Fetch the latest quote for `symbol` from Finnhub.
            Returns a dict with:
            - symbol (str)
            - price (float)
            - timestamp (datetime)
            - provider (str)
            - raw (dict)  # the raw JSON response
        """
        resp = self.client.quote(symbol)
        price = resp["c"]
        ts = datetime.fromtimestamp(resp["t"])

        return {
            "symbol":    symbol,
            "price":     price,
            "timestamp": ts,
            "provider":  "finnhub",
            "raw":       resp,
        }
