# backend/app/models/price_history.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PriceHistoryModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    product_id: str
    price: float
    timestamp: datetime

    class Config:
        allow_population_by_field_name = True
