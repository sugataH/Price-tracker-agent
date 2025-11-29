# app/scrapers/croma_scraper.py

import httpx
from bs4 import BeautifulSoup
from .base import BaseScraper

class CromaScraper(BaseScraper):

    async def scrape(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            name_el = soup.select_one("h1")
            name = name_el.get_text(strip=True) if name_el else None

            price_el = soup.select_one(".pdpPrice")
            if price_el:
                price = float(price_el.get_text(strip=True).replace("₹", "").replace(",", ""))
            else:
                price = None

            return {
                "price": price,
                "name": name,
                "status": "ok" if price else "error"
            }

        except Exception:
            return {"price": None, "name": None, "status": "error"}
