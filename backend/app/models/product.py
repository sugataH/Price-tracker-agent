# backend/app/models/product.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    product_url: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    target_price: Optional[float] = None
    current_price: Optional[float] = None
    lowest_price: Optional[float] = None
    last_checked: Optional[datetime] = None
    status: Optional[str] = "ok"
    name: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
