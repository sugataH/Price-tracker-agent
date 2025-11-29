# app/scrapers/amazon_scraper.py

import httpx
from bs4 import BeautifulSoup
from .base import BaseScraper

class AmazonScraper(BaseScraper):

    async def scrape(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.5"
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract product title
            title_el = soup.select_one("#productTitle")
            name = title_el.get_text(strip=True) if title_el else None

            # Extract price
            price_el = soup.select_one(".a-price .a-offscreen")
            if price_el:
                price_text = price_el.get_text(strip=True)
                price = float(price_text.replace("₹", "").replace(",", ""))
            else:
                price = None

            return {
                "price": price,
                "name": name,
                "status": "ok" if price else "error"
            }

        except Exception as e:
            return {"price": None, "name": None, "status": "error"}
