# backend/app/scrapers/base.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> dict:
        """
        Return dict with keys:
          - price (float or None)
          - name (str or None)
          - status ("ok"|"error")
        """
        raise NotImplementedError
