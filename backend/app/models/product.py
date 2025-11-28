from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

     # Existing column: product_url (keep as-is)
    product_url = Column(String, nullable=False)

    # NEW Phase-2 fields
    target_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    last_checked = Column(DateTime, default=None)
    status = Column(String, default="ok")              # ok / drop / error
    name = Column(String, nullable=True)               # extracted product name

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product")
    sources = relationship("ProductSource", back_populates="product")