from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper
from .croma_scraper import CromaScraper

SCRAPER_MAP = {
    "amazon": AmazonScraper(),
    "flipkart": FlipkartScraper(),
    "croma": CromaScraper()
}

async def scrape_price(source: str, url: str):
    scraper = SCRAPER_MAP.get(source)
    if not scraper:
        return {"price": None, "name": None, "status": "error"}
    return await scraper.scrape(url)
