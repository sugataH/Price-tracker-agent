# backend/app/test_db.py

import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def test_connection():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            print("DB Connected! Result:", result.scalar())
    except Exception as e:
        print("DB ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test_connection())
