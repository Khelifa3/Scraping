import asyncio
import cloudscraper
from bs4 import BeautifulSoup
import re
import time
import asyncDb
import logging
from requests.exceptions import ChunkedEncodingError, RequestException


# Number of retries and delay settings
retries = 2
delay = 5
max_concurrent_tasks = 2

# Configure logging
logging.basicConfig(
    filename="scraper.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s;%(levelname)s;%(message)s",
)
logger = logging.getLogger(__name__)

# Scraper instance
scraper = cloudscraper.create_scraper()
api_url = "https://www.daparto.de/api/Angebote"

# Regex patterns for performance
CATEGORY_PATTERN = re.compile(r"--\d+$")
SPARE_PART_PATTERN = lambda x: re.compile(rf'"(\w+_{x})"')

# Counters for statistics
link_scraped = 0
link_failed = 0


def get_spare_part_id(url, text):
    """Extract the sparePartId based on the URL and page content."""
    x = url.split("/")[-1]
    matches = SPARE_PART_PATTERN(x).findall(text)
    return matches[-1] if matches else None


def get_category_id(soup):
    """Extract the categoryId from the page's breadcrumb link."""
    breadcrumb_link = soup.find("a", href=CATEGORY_PATTERN)
    if breadcrumb_link:
        url = breadcrumb_link["href"]
        return re.search(r"--(\d+)$", url).group(1)
    return None


def parse_json(data):
    """Parse JSON data to extract sellers' information."""
    return [
        [seller["shop"]["name"], seller["price"], seller["totalPrice"]]
        for seller in data
    ]


async def fetch_with_cloudscraper(
    url,
    method="GET",
    params=None,
    headers=None,
    retries=retries,
    delay=delay,
    timeout=10,
):
    """Fetch URL with cloudscraper"""

    def make_request():
        # Set temporary headers if provided
        if headers:
            for key, value in headers.items():
                scraper.headers[key] = value
        try:
            response = scraper.request(method, url, params=params, timeout=timeout)
            return response
        except ChunkedEncodingError as e:
            logger.error(f"ChunkedEncodingError: {e} for URL: {url}")
            return None
        except RequestException as e:
            logger.error(f"RequestException: {e} for URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Exception: {e} for URL: {url}")
            return None

    for attempt in range(retries):
        response = await asyncio.get_running_loop().run_in_executor(None, make_request)
        # Ensure response is valid and has a status code
        if response:
            status_code = response.status_code
            if status_code == 200:
                logger.info(f"200 OK - Successfully acceced URL: {url}")
                return response
            elif status_code == 403:
                logger.error(
                    f"403 Forbidden - Attempt {attempt + 1}/{retries} for URL: {url}"
                )
                await asyncio.sleep(delay)
            elif status_code == 404:
                logger.error(
                    f"404 Not Found - Attempt {attempt + 1}/{retries} for URL: {url}"
                )
                await asyncio.sleep(delay)
            else:
                # Log truly unexpected status codes here
                logger.warning(f"{status_code} - Unexpected status code for URL: {url}")
                break  # Break only on truly unexpected status
        else:
            # Handle cases with no response due to errors
            logger.error(
                f"Attempt {attempt + 1}/{retries} for URL: {url} due to connection error or premature response."
            )
            await asyncio.sleep(delay)

    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return None


async def process_url(pool, product_name, url):
    """Process a single URL by first fetching the HTML, then calling the API and saving data."""
    global link_scraped, link_failed

    # Step 1: Initial request to get sparePartId and categoryId
    response = await fetch_with_cloudscraper(url)
    if response and response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Get categoryId and sparePartId
        category_id = get_category_id(soup)
        spare_part_id = get_spare_part_id(url, response.text)
        if not spare_part_id or not category_id:
            logger.error(f"Missing sparePartId or categoryId for URL: {url}")
            link_failed += 1
            print_status()
            return

        # Step 2: API request using extracted parameters, with referer header
        params = {"sparePartId": spare_part_id, "categoryId": category_id}
        headers = {"referer": url}
        api_response = await fetch_with_cloudscraper(
            api_url, params=params, headers=headers
        )

        if api_response and api_response.status_code == 200:
            data = api_response.json()
            sellers = parse_json(data)

            # Save product, sellers, and prices to the database
            await asyncDb.insert_product(pool, product_name, url)
            for seller_name, price, total_price in sellers:
                await asyncDb.insert_seller(pool, seller_name)
                await asyncDb.insert_price(
                    pool, price, total_price, product_name, seller_name
                )

            link_scraped += 1
            logger.info(f"Successfully scraped and saved data for {url}")
        else:
            logger.error(f"API request failed for {api_url} with params {params}")
            link_failed += 1
    else:
        logger.error(f"Initial request failed for {url}")
        link_failed += 1

    print_status()


def print_status():
    """Print the current count of scraped and failed links on the same line."""
    print(f"\rScraped: {link_scraped} | Failed: {link_failed}", end="")


async def main():
    """Main function to manage concurrent processing of URLs and database connections."""
    db_pool = await asyncDb.create_pool()

    # Load URLs from the file
    with open("links.csv", "r", encoding="utf-8") as file:
        urls = [
            (line.strip().split(";")[0], line.strip().split(";")[1])
            for line in file.readlines()[1:]
        ]

    # Limit concurrent tasks
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def limited_process_url(product_name, url):
        async with semaphore:
            await process_url(db_pool, product_name, url)

    # Run tasks concurrently with a limit
    tasks = [limited_process_url(product_name, url) for product_name, url in urls]
    await asyncio.gather(*tasks)

    # Close the pool after all operations are done
    await asyncDb.close_pool(db_pool)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"\nTotal time taken: {end - start:.2f} seconds")
