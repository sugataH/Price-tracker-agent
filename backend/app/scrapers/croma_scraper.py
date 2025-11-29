# backend/app/scrapers/croma_scraper.py
import httpx
from bs4 import BeautifulSoup
from .base import BaseScraper

class CromaScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return {"price": None, "name": None, "status": "error"}

            soup = BeautifulSoup(resp.text, "html.parser")
            title_el = soup.select_one("h1") or soup.select_one(".product-name")
            name = title_el.get_text(strip=True) if title_el else None

            price_el = soup.select_one(".pdpPrice") or soup.select_one(".price")
            if price_el:
                price_text = price_el.get_text(strip=True)
                price = _parse_price(price_text)
            else:
                price = None

            return {"price": price, "name": name, "status": "ok" if price is not None else "error"}
        except Exception as e:
            print("CromaScraper error:", e)
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
