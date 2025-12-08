# backend/app/crud/product.py
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.core.database import get_db

# Helper to convert ObjectId to str
def _id_to_str(doc):
    if not doc:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

class ProductCRUD:
    def __init__(self):
        pass

    async def create(self, product_url: str, target_price: Optional[float] = None, user_email: Optional[str] = None, source: str = "amazon"):
        db = get_db()
        products = db.products
        product_doc = {
            "product_url": product_url,
            "user_email": user_email,
            "user_phone": None,
            "target_price": target_price,
            "current_price": None,
            "lowest_price": None,
            "last_checked": None,
            "status": "ok",
            "name": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        res = await products.insert_one(product_doc)
        product_id = res.inserted_id

        # Insert initial product source
        product_sources = db.product_sources
        await product_sources.insert_one({
            "product_id": product_id,
            "url": product_url,
            "source": source
        })

        return await self.get_by_id(product_id)

    async def list_all(self, limit: int = 100) -> List[dict]:
        db = get_db()
        cursor = db.products.find().sort("created_at", -1).limit(limit)
        docs = []
        async for d in cursor:
            docs.append(_id_to_str(d))
        return docs

    async def get_by_id(self, product_id) -> Optional[dict]:
        db = get_db()
        try:
            _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        except Exception:
            return None
        doc = await db.products.find_one({"_id": _id})
        return _id_to_str(doc)

    async def get_by_objectid(self, oid) -> Optional[dict]:
        db = get_db()
        doc = await db.products.find_one({"_id": oid})
        return _id_to_str(doc)

    async def add_source(self, product_id, url: str, source: str = "amazon"):
        db = get_db()
        _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        res = await db.product_sources.insert_one({
            "product_id": _id,
            "url": url,
            "source": source
        })
        doc = await db.product_sources.find_one({"_id": res.inserted_id})
        return _id_to_str(doc)

    async def get_sources(self, product_id):
        db = get_db()
        _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        cursor = db.product_sources.find({"product_id": _id})
        out = []
        async for d in cursor:
            out.append(_id_to_str(d))
        return out

    async def insert_price_history(self, product_id, price: float):
        db = get_db()
        _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        res = await db.price_history.insert_one({
            "product_id": _id,
            "price": price,
            "timestamp": datetime.utcnow()
        })
        doc = await db.price_history.find_one({"_id": res.inserted_id})
        return _id_to_str(doc)

    async def get_price_history(self, product_id, limit: int = 100):
        db = get_db()
        _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        cursor = db.price_history.find({"product_id": _id}).sort("timestamp", -1).limit(limit)
        out = []
        async for d in cursor:
            out.append(_id_to_str(d))
        return out

    async def update_product_fields(self, product_id, update_dict: dict):
        db = get_db()
        _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        update_dict["updated_at"] = datetime.utcnow()
        await db.products.update_one({"_id": _id}, {"$set": update_dict})
        return await self.get_by_objectid(_id)

    async def delete(self, product_id):
        db = get_db()
        _id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        await db.products.delete_one({"_id": _id})
        await db.product_sources.delete_many({"product_id": _id})
        await db.price_history.delete_many({"product_id": _id})
        return True

product_crud = ProductCRUD()
