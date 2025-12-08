# backend/app/scheduler/jobs.py
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bson import ObjectId

from app.core.database import get_db
from app.scrapers import scrape_price
from app.crud.product import product_crud
from app.alerts.email_alert import send_email_alert
from app.ai.agent import ai_validate_price
from app.services.price_analyzer import PriceAnalyzer
from app.services.secondary_checker import SecondaryChecker

scheduler = AsyncIOScheduler()


async def _process_product_doc(product_doc):
    """
    product_doc is a dict from products collection with 'id' (string) and other fields.
    """
    db = get_db()
    product_oid = ObjectId(product_doc["id"]) if isinstance(product_doc["id"], str) else product_doc["_id"]
    # fetch sources
    sources_cursor = db.product_sources.find({"product_id": product_oid})
    sources = []
    async for s in sources_cursor:
        # convert _id
        s["id"] = str(s["_id"])
        s["product_id"] = str(s["product_id"])
        sources.append(s)

    if not sources:
        print(f"  ⚠ No sources for product {product_doc['id']}")
        return {"status": "no_sources"}

    scraped_results = []
    for s in sources:
        try:
            r = await scrape_price(s.get("source"), s.get("url"))
            r["_source_url"] = s.get("url")
            r["_source_name"] = s.get("source")
            scraped_results.append(r)
        except Exception as e:
            print(f"  ⚠ Scrape error {s.get('url')}: {e}")

    if not scraped_results:
        print(f"  ⚠ Nothing scraped for product {product_doc['id']}")
        return {"status": "nothing_scraped"}

    # Ask AI agent to validate and structure
    ai_out = await ai_validate_price(product_doc.get("name", ""), scraped_results)

    final_price = ai_out.get("price")
    final_name = ai_out.get("name") or product_doc.get("name")
    final_status = ai_out.get("status", "error")

    # update product
    update_fields = {
        "current_price": final_price,
        "last_checked": datetime.utcnow(),
        "status": final_status
    }
    if final_name:
        update_fields["name"] = final_name

    await product_crud.update_product_fields(product_doc["id"], update_fields)

    # insert into price_history if price exists
    if final_price is not None:
        await product_crud.insert_price_history(product_doc["id"], final_price)

    # analysis
    db = get_db()
    analyzer = PriceAnalyzer(db, near_threshold=0.05)
    # PriceAnalyzer expects a session-like object; we will call analyze with product_doc post-update
    # re-fetch updated product
    updated = await product_crud.get_by_id(product_doc["id"])
    analysis = await analyzer.analyze(updated, final_price)

    # secondary verification
    checker = SecondaryChecker()
    sec = checker.verify({"name": final_name, "price": final_price}, scraped_results, name_threshold=0.68, price_tolerance=0.08)

    primary_alert = analysis.get("alert", False)
    secondary_confirm = sec.get("confirmed", False)

    primary_source_url = scraped_results[0].get("_source_url") if scraped_results else product_doc.get("product_url", "")

    if (primary_alert or secondary_confirm) and product_doc.get("user_email"):
        try:
            await send_email_alert(
                to_email=product_doc.get("user_email"),
                product_name=final_name or "Product",
                product_url=primary_source_url,
                old_price=analysis.get("previous_lowest"),
                new_price=final_price,
                near=analysis.get("near_low", False)
            )
        except Exception as e:
            print(f"  ⚠ Email send failed: {e}")

    return {"status": "processed", "product_id": product_doc["id"], "final_price": final_price, "ai_explain": ai_out.get("explain")}


async def run_check_for_product_by_id(product_id: str):
    prod = await product_crud.get_by_id(product_id)
    if not prod:
        return {"status": "not_found"}
    return await _process_product_doc(prod)


async def run_full_check_now():
    db = get_db()
    cursor = db.products.find()
    results = []
    async for p in cursor:
        p["id"] = str(p["_id"])
        results.append(await _process_product_doc(p))
    return results


async def check_all_prices():
    print("⏱ Scheduler run started")
    await run_full_check_now()
    print("✔ Scheduler run finished")


def start_scheduler():
    scheduler.add_job(check_all_prices, "interval", minutes=5, id="price_checker")
    scheduler.start()
    print("⏱ APScheduler started (every 5 minutes)")
