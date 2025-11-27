from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    url: str

class ProductOut(BaseModel):
    id: int
    name: str
    url: str
    current_price: float | None = None

    class Config:
        from_attributes = True
