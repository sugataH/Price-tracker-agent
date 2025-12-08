# backend/app/models/product_source.py
from pydantic import BaseModel, Field
from typing import Optional

class ProductSourceModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    product_id: str
    url: str
    source: str
