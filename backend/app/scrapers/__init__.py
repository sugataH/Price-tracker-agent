# backend/app/scrapers/__init__.py
from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper
from .croma_scraper import CromaScraper

SCRAPER_MAP = {
    "amazon": AmazonScraper(),
    "flipkart": FlipkartScraper(),
    "croma": CromaScraper()
}

async def scrape_price(source: str, url: str):
    scraper = SCRAPER_MAP.get((source or "").lower())
    if not scraper:
        return {"price": None, "name": None, "status": "error", "explain": "no_scraper_for_source"}
    return await scraper.scrape(url)
