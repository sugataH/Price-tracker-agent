from motor.motor_asyncio import AsyncIOMotorClient
from app.core.settings import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        uri = settings.database_url
        if not uri:
            raise RuntimeError("database_url not set in .env or settings.py")
        _client = AsyncIOMotorClient(uri)
    return _client


def get_db():
    """
    Returns the MongoDB database instance.
    """
    client = get_client()
    db_name = settings.mongo_db_name
    if not db_name:
        raise RuntimeError("mongo_db_name not set in .env or settings.py")
    return client[db_name]
