# backend/app/crud/product.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Product, ProductSource, PriceHistory

class ProductCRUD:
    async def create(self, db: AsyncSession, *, product_url: str, target_price: float = None, user_email: str = None):
        product = Product(product_url=product_url, target_price=target_price, user_email=user_email)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    async def list_all(self, db: AsyncSession):
        result = await db.execute(select(Product))
        return result.scalars().all()

    async def get(self, db: AsyncSession, product_id: int):
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalars().first()

    async def add_source(self, db: AsyncSession, product_id: int, url: str, source: str):
        src = ProductSource(product_id=product_id, url=url, source=source)
        db.add(src)
        await db.commit()
        await db.refresh(src)
        return src

    async def get_sources(self, db: AsyncSession, product_id: int):
        result = await db.execute(select(ProductSource).where(ProductSource.product_id == product_id))
        return result.scalars().all()

    async def get_history(self, db: AsyncSession, product_id: int, limit: int = 100):
        result = await db.execute(select(PriceHistory).where(PriceHistory.product_id == product_id).order_by(PriceHistory.timestamp.desc()).limit(limit))
        return result.scalars().all()

product_crud = ProductCRUD()
