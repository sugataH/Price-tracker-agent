# backend/app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.settings import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        uri = settings.mongo_uri or settings.MONGO_URI if hasattr(settings, "MONGO_URI") else None
        if not uri:
            raise RuntimeError("MONGO_URI not set in environment (.env)")
        _client = AsyncIOMotorClient(uri)
    return _client


def get_db():
    """
    Return the Motor database instance. This is a synchronous accessor used inside async functions.
    Use inside async endpoints like:
        db = get_db()
        collection = db.products
    """
    client = get_client()
    db_name = settings.mongo_db if getattr(settings, "mongo_db", None) else getattr(settings, "MONGO_DB", None)
    if not db_name:
        raise RuntimeError("mongo_db not set in settings")
    return client[db_name]
