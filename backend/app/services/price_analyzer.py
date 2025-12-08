# backend/app/services/price_analyzer.py
from typing import Optional
from datetime import datetime
from app.core.database import get_db

class PriceAnalyzer:
    def __init__(self, db, near_threshold: float = 0.05):
        """
        db is a Motor Database instance from get_db()
        """
        self.db = db
        self.near_threshold = near_threshold

    async def get_all_time_lowest(self, product_id: str):
        oid = product_id
        # product_id passed as string id
        try:
            from bson import ObjectId
            oid = ObjectId(product_id)
        except Exception:
            pass
        doc = await self.db.price_history.find_one({"product_id": oid}, sort=[("price", 1)])
        if doc:
            return doc.get("price")
        return None

    async def update_lowest_if_needed(self, product, current_price: Optional[float]):
        previous_low = product.get("lowest_price")
        if previous_low is None:
            previous_low = await self.get_all_time_lowest(product["id"])

        if current_price is None:
            return False, previous_low

        if previous_low is None or current_price < previous_low:
            # update product lowest_price field
            await self.db.products.update_one({"_id": ObjectId(product["id"])}, {"$set": {"lowest_price": current_price}})
            return True, previous_low

        return False, previous_low

    def is_near_low(self, current_price: float, last_lowest: float):
        if current_price is None or last_lowest is None:
            return False
        return current_price <= last_lowest * (1 + self.near_threshold)

    async def analyze(self, product, final_price: float):
        """
        product: dict from products collection, must have 'id'
        """
        if final_price is None:
            return {"alert": False, "new_low": False, "near_low": False, "previous_lowest": product.get("lowest_price")}

        previous_low = product.get("lowest_price")
        if previous_low is None:
            previous_low = await self.get_all_time_lowest(product["id"])

        new_low, prev = await self.update_lowest_if_needed(product, final_price)
        if previous_low is None:
            previous_low = prev

        near_low = self.is_near_low(final_price, previous_low) if previous_low is not None else False

        target_price = product.get("target_price", None)
        target_hit = target_price is not None and final_price <= target_price

        alert = new_low or near_low or target_hit

        return {"alert": alert, "new_low": new_low, "near_low": near_low, "previous_lowest": previous_low, "target_hit": target_hit}
