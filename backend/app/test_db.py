"""
from app.core.database import SessionLocal
from app.models.product import Product

def test_connection():
    db = SessionLocal()
    try:
        result = db.query(Product).first()
        print("DB connected successfully!")
        print("Sample product:", result)
    except Exception as e:
        print("DB error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
"""

import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def test_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        print("DB Connected! Result:", result.scalar())

if __name__ == "__main__":
    asyncio.run(test_connection())
