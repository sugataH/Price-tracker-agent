# app/scrapers/flipkart_scraper.py

import httpx
from bs4 import BeautifulSoup
from .base import BaseScraper

class FlipkartScraper(BaseScraper):

    async def scrape(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            title_el = soup.select_one("span.VU-ZEz")
            name = title_el.get_text(strip=True) if title_el else None

            price_el = soup.select_one("div.Nx9bqj")
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
