import asyncpg
import asyncio
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    filename="scraper.log",
    encoding="utf-8",
    level=logging.ERROR,
    format="%(asctime)s;%(levelname)s;%(message)s",
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "database": "daparto",
    "host": "localhost",
    "user": "user",
    "password": "password",
    "port": "5432",
}


# Database connection pool functions
async def create_pool():
    """Create a connection pool for the database."""
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        logger.info("Database connection pool created.")
        return pool
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        raise


async def close_pool(pool):
    """Close the database connection pool."""
    await pool.close()
    logger.info("Database connection pool closed.")


# DDL functions
async def create_table_products(pool):
    """Create the products table if it doesn't exist."""
    async with pool.acquire() as conn:
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE,
                url TEXT
            )"""
        )


async def create_table_sellers(pool):
    """Create the sellers table if it doesn't exist."""
    async with pool.acquire() as conn:
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS sellers (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE
            )"""
        )


async def create_table_prices(pool):
    """Create the prices table if it doesn't exist."""
    async with pool.acquire() as conn:
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS prices (
                id SERIAL PRIMARY KEY,
                price FLOAT NOT NULL,
                price_total FLOAT NOT NULL,
                product_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL,
                UNIQUE (product_id, seller_id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (seller_id) REFERENCES sellers (id)
            )"""
        )


# Data manipulation functions
async def insert_product(pool, name: str, url: str):
    """Insert a new product into the products table."""
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO products (name, url) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                name,
                url,
            )
            logger.info(f"Inserted product: {name}")
        except Exception as e:
            logger.error(f"Error inserting product {name}: {e}")


async def insert_seller(pool, name: str):
    """Insert a new seller into the sellers table."""
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO sellers (name) VALUES ($1) ON CONFLICT DO NOTHING",
                name,
            )
            logger.info(f"Inserted seller: {name}")
        except Exception as e:
            logger.error(f"Error inserting seller {name}: {e}")


async def insert_price(
    pool, price: float, price_total: float, product_name: str, seller_name: str
):
    """Insert or update a price entry with foreign keys for product and seller."""
    sql = """INSERT INTO prices (price, price_total, product_id, seller_id)
             VALUES ($1, $2,
                     (SELECT id FROM products WHERE name=$3),
                     (SELECT id FROM sellers WHERE name=$4))
             ON CONFLICT (product_id, seller_id) DO UPDATE
                SET price = $5, price_total = $6"""
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                sql, price, price_total, product_name, seller_name, price, price_total
            )
            logger.info(
                f"Inserted/updated price for product: {product_name}, seller: {seller_name}"
            )
        except Exception as e:
            logger.error(
                f"Error inserting price for product {product_name} and seller {seller_name}: {e}"
            )


async def select_all(
    pool, table: str, order_by: str = "id"
) -> Tuple[List[str], List[asyncpg.Record]]:
    """Return all rows from a specified table."""
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(f"SELECT * FROM {table} ORDER BY {order_by}")
            col_names = [desc[0] for desc in rows[0].keys()] if rows else []
            return col_names, rows
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            return ["error"], []


# Initialization function
async def setup_database(pool):
    """Initialize the database tables if they don't exist."""
    await create_table_products(pool)
    await create_table_sellers(pool)
    await create_table_prices(pool)


# Main function for testing
async def get_product_prices(pool):
    """Fetch all prices related to each product."""
    async with pool.acquire() as conn:
        try:
            query = """
                SELECT p.name AS product_name, s.name AS seller_name, pr.price, pr.price_total
                FROM prices pr
                JOIN products p ON pr.product_id = p.id
                JOIN sellers s ON pr.seller_id = s.id
                ORDER BY p.name, s.name
            """
            rows = await conn.fetch(query)
            result = {}
            for row in rows:
                product_name = row["product_name"]
                if product_name not in result:
                    result[product_name] = []
                result[product_name].append(
                    {
                        "seller_name": row["seller_name"],
                        "price": row["price"],
                        "price_total": row["price_total"],
                    }
                )
            return result
        except Exception as e:
            logger.error(f"Error fetching product prices: {e}")
            return {}


async def main():
    pool = await create_pool()
    await setup_database(pool)  # Ensure tables are created
    product_prices = await get_product_prices(pool)
    n_prices = 0
    for product, prices in product_prices.items():
        print(f"Product: {product}")
        for price_info in prices:
            n_prices += 1
            print(
                f"\tSeller: {price_info['seller_name']}, Price: {price_info['price']}, Total Price: {price_info['price_total']}"
            )
    print(f"{len(product_prices)} total products and {n_prices} prices")
    await close_pool(pool)


if __name__ == "__main__":
    asyncio.run(main())
