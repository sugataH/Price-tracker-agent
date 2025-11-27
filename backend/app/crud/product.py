from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.product import Product
from app.schemas.product import ProductCreate

class ProductCRUD:
    async def create(self, db: AsyncSession, product: ProductCreate):
        db_product = Product(
            name=product.name,
            url=product.url,
            current_price=None
        )
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product

    async def list_all(self, db: AsyncSession):
        result = await db.execute(select(Product))
        return result.scalars().all()

product_crud = ProductCRUD()
