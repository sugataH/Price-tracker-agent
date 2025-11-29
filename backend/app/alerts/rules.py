# backend/app/alerts/rules.py
from sqlalchemy import select
from app.models import PriceHistory

async def should_trigger_alert(session, product, new_price, source_name=None):
    """
    Old-style rule engine kept for compatibility.
    Returns (bool, reason_str)
    """
    if new_price is None:
        return False, None

    target_price = getattr(product, "target_price", None)
    if source_name and source_name.lower() == "amazon" and target_price is not None and new_price <= target_price:
        return True, "primary_target_hit"

    if target_price is not None and new_price <= target_price:
        return True, "target_hit"

    # fetch lowest historic price
    q = await session.execute(select(PriceHistory).where(PriceHistory.product_id == product.id).order_by(PriceHistory.price.asc()).limit(1))
    row = q.scalars().first()
    if row:
        last_low = row.price
        if new_price <= last_low * 1.05:
            return True, "near_all_time_low"

    return False, None
