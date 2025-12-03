# backend/app/api/product_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.crud.product import product_crud
from app.models import Product, ProductSource

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", status_code=201)
async def create_product(payload: dict, db: AsyncSession = Depends(get_db)):
    product_url = payload.get("product_url")
    if not product_url:
        raise HTTPException(status_code=400, detail="product_url required")
    product = await product_crud.create(db, product_url=product_url, target_price=payload.get("target_price"), user_email=payload.get("user_email"))
    # add initial source
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

@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await product_crud.get(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    return {
        "id": p.id,
        "product_url": p.product_url,
        "name": p.name,
        "current_price": p.current_price,
        "target_price": p.target_price,
        "last_checked": p.last_checked,
        "status": p.status,
        "user_email": p.user_email
    }

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await product_crud.get(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    await db.delete(p)
    await db.commit()
    return {"ok": True, "deleted": product_id}

@router.post("/{product_id}/sources", status_code=201)
async def add_product_source(product_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    url = payload.get("url")
    source = payload.get("source", "amazon")
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    src = await product_crud.add_source(db, product_id, url, source)
    return {"id": src.id, "product_id": src.product_id, "url": src.url, "source": src.source}
