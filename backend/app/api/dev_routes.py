# backend/app/api/dev_routes.py
"""
test scrapers, send a test email (verifies SMTP), trigger scheduler run manually, and force sync a product.
"""
# backend/app/api/dev_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.core.database import get_db, AsyncSessionLocal
from app.scrapers import scrape_price
from app.alerts.email_alert import send_email_alert
from app.crud.product import product_crud
from app.scheduler.jobs import _run_check_for_product, check_all_prices

router = APIRouter(prefix="/dev", tags=["dev"])

@router.get("/scrape")
async def dev_scrape(source: str, url: str):
    """
    Quick scraper test:
    GET /dev/scrape?source=amazon&url=https://...
    """
    result = await scrape_price(source, url)
    return {"ok": True, "source": source, "url": url, "result": result}

@router.post("/send-test-email")
async def dev_send_test_email(payload: dict):
    """
    JSON body:
    { "to_email": "you@example.com", "subject": "optional", "body": "html or text" }
    """
    to = payload.get("to_email")
    if not to:
        raise HTTPException(status_code=400, detail="to_email required")
    product_name = payload.get("product_name", "Test Product")
    product_url = payload.get("product_url", "https://example.com")
    old_price = payload.get("old_price", 1000)
    new_price = payload.get("new_price", 900)
    near = bool(payload.get("near", False))

    await send_email_alert(to, product_name, product_url, old_price, new_price, near)
    return {"ok": True, "sent_to": to}

@router.post("/run-scheduler-now")
async def dev_run_scheduler_now():
    """
    Trigger scheduler run immediately (useful for testing)
    """
    # run check_all_prices once in background
    await check_all_prices()
    return {"ok": True, "ran": datetime.utcnow().isoformat()}

@router.post("/sync-product/{product_id}")
async def dev_sync_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Force run check for a single product via _run_check_for_product
    """
    product = await product_crud.get(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    # _run_check_for_product accepts (session, product)
    await _run_check_for_product(db, product)
    return {"ok": True, "product_id": product_id}
