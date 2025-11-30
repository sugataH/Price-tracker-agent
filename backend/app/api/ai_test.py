# backend/app/api/ai_test.py

from fastapi import APIRouter
from app.ai.agent import ai_validate_price

router = APIRouter()

@router.get("/ai-test")
async def ai_test():
    scraped = [
        {
            "name": "Test Product",
            "price": 999,
            "rating": 4.5,
            "availability": "in stock"
        }
    ]

    result = await ai_validate_price("Test Product", scraped)

    return {
        "status": "AI working",
        "input": scraped,
        "output": result
    }
