# backend/app/api/history_routes.py
from fastapi import APIRouter, HTTPException
from app.crud.product import product_crud

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/product/{product_id}")
async def get_history(product_id: str, limit: int = 100):
    product = await product_crud.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    hist = await product_crud.get_price_history(product_id, limit)
    # return history in chronological order (oldest first)
    return list(reversed(hist))
