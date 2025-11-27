from sqlalchemy import Column, Integer, String, Float
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    current_price = Column(Float, nullable=True)
