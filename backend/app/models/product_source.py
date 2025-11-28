from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class ProductSource(Base):
    __tablename__ = "product_sources"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))

    url = Column(String, nullable=False)    # Amazon / Flipkart / etc.
    source = Column(String, nullable=False) # amazon / flipkart / croma / myntra…

    product = relationship("Product", back_populates="sources")
