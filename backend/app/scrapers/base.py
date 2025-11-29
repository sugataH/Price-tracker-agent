# backend/app/scrapers/base.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> dict:
        """
        Return dict with keys:
          - price (float|None)
          - name (str|None)
          - status ("ok"|"error")
        """
        raise NotImplementedError
