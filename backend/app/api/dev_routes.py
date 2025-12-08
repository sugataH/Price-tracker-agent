# backend/app/api/dev_routes.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.scrapers import scrape_price
from app.alerts.email_alert import send_email_alert
from app.crud.product import product_crud
from app.scheduler.jobs import run_full_check_now, run_check_for_product_by_id

router = APIRouter(prefix="/dev", tags=["dev"])

@router.get("/scrape")
async def dev_scrape(source: str, url: str):
    result = await scrape_price(source, url)
    return {"ok": True, "source": source, "url": url, "result": result}

@router.post("/send-test-email")
async def dev_send_test_email(payload: dict):
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
    await run_full_check_now()
    return {"ok": True, "ran": datetime.utcnow().isoformat()}

@router.post("/sync-product/{product_id}")
async def dev_sync_product(product_id: str):
    res = await run_check_for_product_by_id(product_id)
    return {"ok": True, "product_id": product_id, "result": res}
