# backend/app/models/product.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # URL the user submitted as primary product link
    product_url = Column(String, nullable=False)

    # Optional user contact + metadata
    user_email = Column(String, nullable=True)
    user_phone = Column(String, nullable=True)

    # Tracking fields
    target_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    lowest_price = Column(Float, nullable=True)
    last_checked = Column(DateTime, default=None)
    status = Column(String, default="ok")  # ok / drop / error
    name = Column(String, nullable=True)

    # relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
