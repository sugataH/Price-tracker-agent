# backend/app/models/product.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    product_url = Column(String, nullable=False)

    user_email = Column(String, nullable=True)
    user_phone = Column(String, nullable=True)

    target_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    lowest_price = Column(Float, nullable=True)
    last_checked = Column(DateTime, default=None)
    status = Column(String, default="ok")
    name = Column(String, nullable=True)

    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
