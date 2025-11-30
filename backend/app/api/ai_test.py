from fastapi import APIRouter
from app.ai.agent import ai_validate_price

router = APIRouter()

@router.get("/ai-test")
async def ai_test():
    test_scraped_results = [
        {
            "name": "Test Product",
            "price": 999,
            "rating": 4.5,
            "availability": "in stock"
        }
    ]

    result = await ai_validate_price("Test Product", test_scraped_results)

    return {
        "status": "AI working",
        "input": test_scraped_results,
        "output": result
    }
