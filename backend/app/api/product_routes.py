# backend/app/api/product_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.product import product_crud

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/")
async def create_product(payload: dict, db: AsyncSession = Depends(get_db)):
    product_url = payload.get("product_url")
    if not product_url:
        raise HTTPException(status_code=400, detail="product_url required")
    product = await product_crud.create(db, product_url=product_url, target_price=payload.get("target_price"), user_email=payload.get("user_email"))
    await product_crud.add_source(db, product.id, product_url, payload.get("source", "amazon"))
    return {"id": product.id, "product_url": product.product_url}

@router.get("/")
async def list_products(db: AsyncSession = Depends(get_db)):
    prods = await product_crud.list_all(db)
    out = []
    for p in prods:
        out.append({
            "id": p.id,
            "product_url": p.product_url,
            "name": p.name,
            "current_price": p.current_price,
            "target_price": p.target_price,
            "last_checked": p.last_checked,
            "status": p.status,
            "user_email": p.user_email
        })
    return out

@router.get("/{product_id}/sync")
async def sync_product(product_id: int, db: AsyncSession = Depends(get_db)):
    from app.scheduler.jobs import _run_check_for_product
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    await _run_check_for_product(db, product)
    return {"status": "ok"}
