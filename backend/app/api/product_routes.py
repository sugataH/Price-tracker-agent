# backend/app/api/product_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from app.crud.product import product_crud

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", status_code=201)
async def create_product(payload: dict):
    product_url = payload.get("product_url")
    if not product_url:
        raise HTTPException(status_code=400, detail="product_url required")
    product = await product_crud.create(
        product_url=product_url,
        target_price=payload.get("target_price"),
        user_email=payload.get("user_email"),
        source=payload.get("source", "amazon")
    )
    return {"id": product["id"], "product_url": product["product_url"]}

@router.get("/")
async def list_products():
    prods = await product_crud.list_all()
    return prods

@router.get("/{product_id}")
async def get_product(product_id: str):
    p = await product_crud.get_by_id(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    return p

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    p = await product_crud.get_by_id(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    await product_crud.delete(product_id)
    return {"ok": True, "deleted": product_id}

@router.post("/{product_id}/sources", status_code=201)
async def add_product_source(product_id: str, payload: dict):
    url = payload.get("url")
    source = payload.get("source", "amazon")
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    src = await product_crud.add_source(product_id, url, source)
    return {"id": src["id"], "product_id": src["product_id"], "url": src["url"], "source": src["source"]}

@router.get("/{product_id}/sync")
async def sync_product(product_id: str):
    """
    Triggers a sync for a single product — calls scheduler helper.
    """
    from app.scheduler.jobs import run_check_for_product_by_id
    res = await run_check_for_product_by_id(product_id)
    return {"status": "ok", "result": res}
