# backend/app/scrapers/amazon_scraper.py
import httpx
from bs4 import BeautifulSoup
from .base import BaseScraper

class AmazonScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "Accept-Language": "en-US,en;q=0.9"
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return {"price": None, "name": None, "status": "error"}

            soup = BeautifulSoup(resp.text, "html.parser")
            title_el = soup.select_one("#productTitle")
            name = title_el.get_text(strip=True) if title_el else None

            price_el = soup.select_one(".a-price .a-offscreen")
            if not price_el:
                price_el = soup.select_one("#priceblock_ourprice") or soup.select_one("#priceblock_dealprice")

            if price_el:
                price_text = price_el.get_text(strip=True)
                price = _parse_price(price_text)
            else:
                price = None

            return {"price": price, "name": name, "status": "ok" if price is not None else "error"}
        except Exception as e:
            print("AmazonScraper error:", e)
            return {"price": None, "name": None, "status": "error"}

def _parse_price(txt: str):
    if not txt:
        return None
    try:
        cleaned = txt.replace("₹", "").replace(",", "").strip()
        cleaned = ''.join(ch for ch in cleaned if (ch.isdigit() or ch == '.'))
        return float(cleaned) if cleaned else None
    except Exception:
        return None
