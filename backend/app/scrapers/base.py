# app/scrapers/base.py

from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Base class for all scrapers."""

    @abstractmethod
    async def scrape(self, url: str) -> dict:
        """
        Returns:
            {
                "price": float,
                "name": str,
                "status": "ok" | "error"
            }
        """
        pass
