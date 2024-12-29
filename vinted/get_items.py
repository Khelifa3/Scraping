import aiohttp
import asyncio
import math
import csv
import get_users_by_closet
import scraping_func
import os.path

file_name = "products_vinted.csv"

MAX_CONCURENT = 3  # max 100
TIMEOUT = 10

sem = asyncio.Semaphore(MAX_CONCURENT)
rotate_proxy = scraping_func.RotateProxy("proxies_fr.txt", random=True)
base_url = "https://www.vinted.fr/"
users_url = f"https://www.vinted.fr/api/v2/users?page="
file_exists = os.path.isfile(file_name)
header = [
    "listing_name",
    "materials",
    "color",
    "size",
    "price",
    "currency",
    "product_url",
    "designer",
    "market_place",
    "condition",
    "main_category",
    "sub_category",
    "gender",
    "location",
    "date",
    "image_links",
]
with open(file_name, "a", encoding="utf-8", newline="") as f:
    if not file_exists:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)


def saveItem(item):
    items = item["items"]
    for i in items:
        # listing_name: title, description
        listing_name = i["title"]
        # materials: composition, material
        materials = i["material"]
        # color: color1, color2
        color1 = i["color1"] or ""
        color2 = i["color2"] or ""
        color = f"{color1} {color2}".strip()
        # size: size
        size = i["size"]
        # price: price_numeric, discount_price
        price = i["price_numeric"]
        # currency: currency
        currency = i["currency"]
        # product_url:  path, url
        product_url = i["url"]
        # designer: brand, label
        designer = i["brand"]
        # market_place: vinted ???
        market_place = "vinted"
        # condition: status
        condition = i["status"]
        # path = /gender-age/main_category/sub_category
        path = i["path"].split("/")[1:]
        # main_category: ???
        main_category = path[1]
        # sub_category: ???
        sub_category = path[2]
        # gender: is_unisex, ???
        gender = path[0]
        # location: country
        location = i["country"]
        # date: last_push_up_at, created_at_ts, updated_at_ts, created_at
        date = i["created_at"]
        # image_links: photos[0][url]
        image_links = i["photos"][0]["url"]
        product = [
            listing_name,
            materials,
            color,
            size,
            price,
            currency,
            product_url,
            designer,
            market_place,
            condition,
            main_category,
            sub_category,
            gender,
            location,
            date,
            image_links,
        ]

        with open(file_name, "a", encoding="utf-8", newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(product)


async def getItems(session, user_id, page):
    proxy = rotate_proxy.get()
    try:
        async with session.get(base_url, proxy=proxy, ssl=False) as response:
            if response.status != 200:
                print(f"Exception {response.status}")
                failed.append([user_id, page])
                return None
            await response.text()
    except Exception as e:
        print(f"Exception {repr(e)}")
        failed.append([user_id, page])
        return None

    items_url = f"https://www.vinted.fr/api/v2/users/{user_id}/items?page={page}&per_page={per_page}&order=relevance&currency=EUR"
    async with session.get(
        items_url,
        proxy=proxy,
        ssl=False,
    ) as response:
        if response.status == 200:
            json_response = await response.json()
            print(f"Page {page} from seller {user_id} scraped")
            try:
                saveItem(json_response)
            except Exception as e:
                print(repr(e))
            return user_id
        else:
            failed.append([user_id, page])
            print("status: ", response.status)


async def safe_download(session, user_id, page):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await getItems(session, user_id, page)


async def getUsers(session, users_pages):
    tasks = []
    for user in users_pages:
        user_id, user_pages = user
        for page in range(1, user_pages + 1):
            task = asyncio.create_task(safe_download(session, user_id, page))
            tasks.append(task)

    try:
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.exceptions.TimeoutError:
        print("Timeout!")
    return responses


async def main(users_pages):
    my_timeout = aiohttp.ClientTimeout(total=None, sock_connect=10, sock_read=10)
    client_args = dict(trust_env=True, timeout=my_timeout)

    async with aiohttp.ClientSession(**client_args) as session:
        items = await getUsers(session, users_pages)
        return items


if __name__ == "__main__":
    users = get_users_by_closet.getUsers()
    users_pages = []
    failed = []
    total_item = 0
    for user in users:
        user_id, user_item_count = user, users[user]
        total_item += user_item_count
        per_page = 96  # max items per page
        total_pages = math.ceil((user_item_count / per_page))
        users_pages.append([user_id, total_pages])
    print(f"Scraping {total_item} productcs from {len(users_pages)} sellers...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    items = asyncio.run(main(users_pages))
    while len(failed) > 0:
        print(f"Retrying {len(failed)} failed pages...")
        user_pages = failed
        failed = []
        asyncio.run(main(user_pages))
