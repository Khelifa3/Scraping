import asyncio
import logging
from typing import List, Tuple
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import asyncDb

batch_size = 5
retries = 1  # 1 = only 1 try
timeout = 3000  # time in ms for waiting page to load

# User agent
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81"

# Proxies list
proxies = {
    "server": "geo.iproyal.com:12321",
    "username": "googleShop",
    "password": "oddgoogle12",
}

# Configure logging
logging.basicConfig(
    filename="scraper.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s;%(levelname)s;%(message)s",
)
logger = logging.getLogger(__name__)
products_scraped = 0
url_failed = 0


# Utility to convert prices
def convert_price(price_str: str) -> float:
    """Convert price string to float with proper formatting."""
    return (
        price_str.replace("\xa0", " ").replace(".", "").split(" ")[0].replace(",", ".")
    )


# Async function to fetch content with retry logic
async def fetch_content(url: str, page: Page, retries: int = retries) -> str:
    """Fetch page content, retrying on failure up to 'retries' times."""
    global url_failed
    for attempt in range(retries):
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector("li.offer-list-item", timeout=timeout)
            return await page.content()
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == retries - 1:
                url_failed += 1
                return ""  # Return empty if final attempt fails
            await asyncio.sleep(2)  # Delay before retrying


# Parse and store data within a database transaction
async def parse_and_store_data(content: str, product_name: str, url: str, pool) -> None:
    """Parse seller data and store it in the database as a single transaction."""
    global products_scraped
    sellers_info = extract_sellers(content)
    if sellers_info:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await asyncDb.insert_product(pool, product_name, url)
                for seller_name, price, total_price in sellers_info:
                    await asyncDb.insert_seller(pool, seller_name)
                    await asyncDb.insert_price(
                        pool, price, total_price, product_name, seller_name
                    )
                logger.info(f"Stored data for {product_name} from {url}")
                products_scraped += 1


# Extract sellers data from HTML content
def extract_sellers(content: str) -> List[Tuple[str, float, float]]:
    """Extract seller information from HTML content."""
    soup = BeautifulSoup(content, "html.parser")
    seller_elements = soup.select("li.offer-list-item")
    sellers_info = []
    for seller in seller_elements:
        try:
            seller_name = seller.find("img")["alt"]
            price = convert_price(
                seller.find(class_="value-price").get_text(strip=True)
            )
            total_price_str = seller.find("a").get_text(strip=True)
            total_price = convert_price(total_price_str)
            if total_price.lower() == "kostenloser":  # Handle free shipping
                total_price = price
            sellers_info.append((seller_name, float(price), float(total_price)))
        except (TypeError, AttributeError) as e:
            logger.warning(f"Missing element in seller data: {e}")
    return sellers_info


# Main scraping function for a single URL
async def scrape_url(product_name: str, url: str, pool, page: Page):
    """Fetch and parse content for a single URL, then store data in the database."""
    content = await fetch_content(url, page)
    if content:
        await parse_and_store_data(content, product_name, url, pool)
    await page.close()  # Close page after scraping


# Async function to scrape multiple URLs concurrently
async def scrape_all(urls, pool) -> None:
    """Launch browser and manage concurrent page scraping tasks."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=ua)
        tasks = [
            scrape_url(name, url, pool, await context.new_page())
            for i, (name, url) in enumerate(urls)
        ]
        await asyncio.gather(*tasks)
        await context.close()
        await browser.close()


# Entry point for batch processing
async def main():
    """Main function to load URLs, create database pool, and process URLs in batches."""
    # Create a connection pool
    db_pool = await asyncDb.create_pool()
    # Load URLs from CSV
    with open("links.csv", "r", encoding="utf-8") as file:
        urls = [line.strip().split(";") for line in file.readlines()[7600:7650]]
    # Run scraping in batches
    for i in range(0, len(urls), batch_size):
        batch = urls[i : i + batch_size]
        await scrape_all(batch, db_pool)
        logger.info(f"Batch {i // batch_size + 1} completed.")
        print(f"Scraped {products_scraped} products,  {url_failed} failed..")
    # Close the pool after all operations are done
    await asyncDb.close_pool(db_pool)


if __name__ == "__main__":
    asyncio.run(main())
