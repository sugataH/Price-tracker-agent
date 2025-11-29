# backend/app/api/history_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.product import product_crud

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/product/{product_id}")
async def get_history(product_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)):
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    hist = await product_crud.get_history(db, product_id, limit)
    out = [{"price": h.price, "timestamp": h.timestamp.isoformat()} for h in reversed(hist)]
    return out
