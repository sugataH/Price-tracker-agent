# backend/app/scheduler/jobs.py
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.scrapers import scrape_price
from app.models import Product, ProductSource, PriceHistory
from app.alerts.email_alert import send_email_alert
from app.ai.agent import ai_validate_price
from app.services.price_analyzer import PriceAnalyzer
from app.services.secondary_checker import SecondaryChecker

scheduler = AsyncIOScheduler()

async def _run_check_for_product(session, product):
    print(f"🔍 Checking product id={product.id}")

    q = await session.execute(select(ProductSource).where(ProductSource.product_id == product.id))
    sources = q.scalars().all()

    if not sources:
        print("  ⚠ No sources found, skipping")
        return

    scraped_results = []
    for s in sources:
        try:
            raw = await scrape_price(s.source, s.url)
            raw["_source_url"] = s.url
            raw["_source_name"] = s.source
            scraped_results.append(raw)
        except Exception as e:
            print(f"  ⚠ Error scraping {s.url}: {e}")

    if not scraped_results:
        print("  ⚠ Nothing scraped for this product")
        return

    ai_output = None
    try:
        ai_output = await ai_validate_price(getattr(product, "name", ""), scraped_results)
    except TypeError:
        try:
            ai_output = await ai_validate_price(scraped_results)
        except Exception as e:
            print("  ⚠ AI fallback error:", e)
            ai_output = None
    except Exception as e:
        print("  ⚠ AI error:", e)
        ai_output = None

    if not isinstance(ai_output, dict):
        prices = [r.get("price") for r in scraped_results if isinstance(r.get("price"), (int, float))]
        final_price = min(prices) if prices else None
        name = next((r.get("name") for r in scraped_results if r.get("name")), None)
        ai_output = {"price": final_price, "name": name, "status": "ok" if final_price is not None else "error", "explain": "fallback"}

    final_price = ai_output.get("price")
    final_name = ai_output.get("name") or getattr(product, "name", None)
    final_status = ai_output.get("status", "error")

    product.current_price = final_price
    product.last_checked = datetime.utcnow()
    product.status = final_status
    if final_name:
        product.name = final_name

    if final_price is not None:
        h = PriceHistory(product_id=product.id, price=final_price, timestamp=datetime.utcnow())
        session.add(h)

    analyzer = PriceAnalyzer(session, near_threshold=0.05)
    analysis = await analyzer.analyze(product, final_price)

    await session.commit()

    checker = SecondaryChecker()
    sec = checker.verify({"name": final_name, "price": final_price}, scraped_results, name_threshold=0.68, price_tolerance=0.08)

    primary_alert = analysis.get("alert", False)
    secondary_confirm = sec.get("confirmed", False)

    product_url = scraped_results[0].get("_source_url") if scraped_results and scraped_results[0].get("_source_url") else getattr(product, "product_url", "")

    if primary_alert or secondary_confirm:
        user_email = getattr(product, "user_email", None)
        if user_email:
            try:
                await send_email_alert(
                    to_email=user_email,
                    product_name=final_name or "Product",
                    product_url=product_url,
                    old_price=analysis.get("previous_lowest"),
                    new_price=final_price,
                    near=analysis.get("near_low", False)
                )
            except Exception as e:
                print(f"  ⚠ Failed to send email: {e}")
        else:
            print(f"  ⚠ No user_email set for product {product.id}; skipping email.")

    return

async def check_all_prices():
    print("⏱ Scheduler run started")
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Product))
        products = q.scalars().all()
        for product in products:
            try:
                await _run_check_for_product(session, product)
            except Exception as e:
                print(f"  ⚠ Error processing product {getattr(product, 'id', 'unknown')}: {e}")
    print("✔ Scheduler run finished")

def start_scheduler():
    scheduler.add_job(check_all_prices, "interval", minutes=5, id="price_checker")
    scheduler.start()
    print("⏱ APScheduler started (every 5 minutes)")
