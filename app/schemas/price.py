from pydantic import BaseModel
from datetime import datetime

class PriceResponse(BaseModel):
    """
    In FastAPI, Pydantic models define your request/response shapes.
    from_attributes=True lets Pydantic read directly from ORM attributes.
    """
    symbol: str
    price: float
    timestamp: datetime
    provider: str

    class Config:
        from_attributes = True
