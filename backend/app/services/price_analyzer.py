# backend/app/services/price_analyzer.py
from sqlalchemy import select, func
from app.models import PriceHistory
from datetime import datetime

class PriceAnalyzer:
    def __init__(self, session, near_threshold: float = 0.05):
        self.session = session
        self.near_threshold = near_threshold

    async def get_all_time_lowest(self, product_id: int):
        q = await self.session.execute(
            select(func.min(PriceHistory.price)).where(PriceHistory.product_id == product_id)
        )
        return q.scalar_one_or_none()

    async def update_lowest_if_needed(self, product, current_price: float):
        previous_low = getattr(product, "lowest_price", None)
        if previous_low is None:
            previous_low = await self.get_all_time_lowest(product.id)

        if current_price is None:
            return False, previous_low

        if previous_low is None or current_price < previous_low:
            setattr(product, "lowest_price", current_price)
            return True, previous_low

        return False, previous_low

    def is_near_low(self, current_price: float, last_lowest: float):
        if current_price is None or last_lowest is None:
            return False
        return current_price <= last_lowest * (1 + self.near_threshold)

    async def analyze(self, product, final_price: float):
        if final_price is None:
            return {"alert": False, "new_low": False, "near_low": False, "previous_lowest": getattr(product, "lowest_price", None)}

        previous_low = getattr(product, "lowest_price", None)
        if previous_low is None:
            previous_low = await self.get_all_time_lowest(product.id)

        new_low, prev = await self.update_lowest_if_needed(product, final_price)
        if previous_low is None:
            previous_low = prev

        near_low = self.is_near_low(final_price, previous_low) if previous_low is not None else False

        target_price = getattr(product, "target_price", None)
        target_hit = target_price is not None and final_price <= target_price

        alert = new_low or near_low or target_hit

        return {
            "alert": alert,
            "new_low": new_low,
            "near_low": near_low,
            "previous_lowest": previous_low,
            "target_hit": target_hit
        }
