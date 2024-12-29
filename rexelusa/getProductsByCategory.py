import requests
import json
import process_excel
import logging
import time

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Set up the request headers
headers = {
    "Accept": "application/graphql-response+json, application/graphql+json, application/json, text/event-stream, multipart/mixed",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkFGNkQyNDVBNjhBNTIwQzM3MjcyQjA3RTY5MTI5M0U5RjYyQzZDQzhSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6InIyMGtXbWlsSU1OeWNyQi1hUktUNmZZc2JNZyJ9.eyJuYmYiOjE3MzI4NjYyNjgsImV4cCI6MTczMjkzODI2OCwiaXNzIjoiaHR0cHM6Ly9hdXRoLnJleGVsdXNhLmNvbSIsImF1ZCI6InNmLndlYiIsImNsaWVudF9pZCI6InN0b3JlZnJvbnQtd2ViLXYyIiwic3ViIjoiMjY1NDk5IiwiYXV0aF90aW1lIjoxNzMxNzUwNjMxLCJpZHAiOiJsb2NhbCIsImFjciI6InVucHciLCJ3dWlkIjoia2dhU3pnQUVEUnZBIiwiZGlkIjoiMDBiNDE5ODMtOGE5Zi00ZGI2LWIyMTEtZGEzZjljNDAxODRkIiwianRpIjoiMTY2QThGOTM3OTI4QjI1MkMxRjREMTE2MkNFQjUxMzUiLCJpYXQiOjE3MzI4NjYyNjgsInNjb3BlIjpbInNmLndlYiIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJwd2QiXX0.qqM20ZNmazW7o0dQy04Vjxr3g1o41-LUW5ay_l1UzvSYqEfDghMa1PUArqxq5FVn6t_b8wbLoIk_lVnip_Cl0mXKD6Bp35hATUX1cLBCiuHZPL6TDUIAmUu2Hzxtc2reTP35RSdYXAk-Pdj8oOhqZi7nNK1OBoTc0jkAAeNeYx0dkmgu03cpOc9cnMdQiqkFp2yN9eqrZeBKxx1Ux_fDz-lP3O6z5W60BBhSTsg9Ox8q9WXG0EVod9FuIlQxHc7hkLI0IWHnYx1nZPjtnqSjGhtPJdXD623UTlBa1023ytKWbb2_ucHKK1Regp50E5aSLAPrfjF6GqSa2S0ZQCNTsw",
    "Origin": "https://www.rexelusa.com",
    "Priority": "u=1, i",
    "Referer": "https://www.rexelusa.com/s/electrical-boxes-enclosures?cat=r1i4hp",
    "Sec-CH-UA": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Traceparent": "00-408ddff24c4ec2f2202fc13ff6b4cac5-27faeaf278994bbd-01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}


# API endpoint
api_url = "https://www.rexelusa.com/graphql"
site = "https://www.rexelusa.com"
session = requests.Session()
session.headers = headers
all_categories_file = "allcategory.json"
all_products_file = "productsbycategory.json"
substitus_file = "substite.json"
prices_file = "realTimePrices.json"


def log(message):
    logging.info(message)
    print(message)


def saveProgress(category_code, category_name, page):
    with open("progress.txt", "w") as f:
        str_save = f"{category_code};{category_name};{page}"
        f.write(str_save)


def loadProgres():
    try:
        with open("progress.txt", "r") as f:
            str_save = f.read()
            category_code, category_name, page = str_save.split(";")
            log(f"Loaded progress {category_code} {category_name} {page}")
            return [category_code, category_name, page]
    except Exception as e:
        log("No progress file found, starting from scratch...")
        return None


def query(query_file, variables={}):
    with open(query_file, "r") as f:
        data = json.load(f)
    for v in variables:
        data["variables"][v] = variables[v]

    try:
        response = session.post(
            api_url,
            json=data,
        )
        return response
    except Exception as e:
        log(f"{e} : {query_file}")
        return None


def queryProductsByCategory(query_file, category_code, page=1, page_size=100):
    with open(query_file, "r") as f:
        data = json.load(f)
    data["variables"]["request"]["filter"]["categoryCode"] = category_code
    data["variables"]["request"]["productsPaging"]["page"] = page
    data["variables"]["request"]["productsPaging"]["pageSize"] = page_size
    try:
        response = session.post(
            api_url,
            json=data,
        )
        return response
    except Exception as e:
        log(f"{e} : {query_file}")
        return None


def getCategories():
    response = query(all_categories_file)
    res_json = response.json()
    try:
        categories = res_json["data"]["viewer"]["categoriesRoot"]["nodes"]
    except Exception as e:
        log(f"{e} : categories")
    l_categories = []
    for category in categories:
        code = category["code"]
        shortName = category["shortName"]  # category name
        slug = category["searchUrlInternal"]["slug"]  #
        l_categories.append([code, shortName])
    return l_categories


def getProductsByCategory(category_code, category_name, page=1, page_size=100):
    log(f"Scraping page {page} from {category_name}...")
    response = queryProductsByCategory(
        all_products_file, category_code, page, page_size=100
    )
    # Check if the request was successful and output the response data
    if response and response.status_code == 200:
        res_json = response.json()
        try:
            products = res_json["data"]["viewer"]["customerById"]["productSearchV2"][
                "products"
            ]
        except Exception as e:
            log(f"{e} : {products}")
        total_count = products["totalCount"]
        nodes = products["nodes"]
        file_name = f"rexel_{category_name.lower().replace(' ', '_')}.xlsx"
        wb_obj, sheet_obj = process_excel.openExcel(file_name)
        row = 2
        prices_expired = []
        for node in nodes:
            product = node["product"]
            if product["summary"]["__typename"] == "ProductNotFound":
                continue
            try:
                description = product["summary"]["longDescription"]
            except KeyError as k:
                print(product["summary"])
            title = product["summary"]["title"]
            upc = product["summary"]["upc"]
            productNumber = product["summary"]["productNumber"]
            cat_num = product["summary"]["catNum"]
            routeId = product["summary"]["urlInternal"]["routeId"]
            slug = product["summary"]["urlInternal"]["slug"]  # site/p/routeId/slug
            url = f"{site}/p/{routeId}/{slug}"
            image = product["summary"]["image"]["sq150"]["url"]
            sub_category = product["summary"]["category"]["shortName"]
            try:
                price = product["prices"][0]["price"]["amount"]
            except:  # CACHE_EXPIRED get real time price
                # save row and product to query at the end
                prices_expired.append([row, routeId])
                price = "N/A"

            stock = product["inventoryCompanyWide"]
            try:
                manufacturer = product["summary"]["manufacturer"]["name"]
                m_description = product["summary"]["manufacturer"]["description"]
            except Exception as e:
                manufacturer = "null"
                m_description = "null"
                log(f"{e}, {productNumber}, {manufacturer}")
            attributes = product["summary"]["attributes"]
            data = [
                routeId,
                url,
                site,
                manufacturer,
                cat_num,  # "Manufacturer Part Number",
                m_description,
                "Rexel",  # "Supplier Name",
                routeId,  # "Supplier Part Number",
                image,
                description,
                category_name,  # category
                sub_category,
                "",  # UNSPSC
                upc,
                "",  # note
                price,
                stock,
                "",  # Substitute 1 MFG name
                "",  # Substitute 1 description,
                "",  # Substitute 1 part number
                "",  # Substitute 2 MFG name
                "",  # Substitute 2 description,
                "",  # Substitute 2 part number
                "",  # Substitute 3 MFG name
                "",  # Substitute 3 description,
                "",  # Substitute 3 part number
                "",  # Substitute 4 MFG name
                "",  # Substitute 4 description,
                "",  # Substitute 4 part number
            ]

            for attribute in attributes:
                label = attribute["type"]["displayName"]
                values = attribute["values"]
                values_text = ""
                for value in values:
                    text = value["text"]
                    values_text += f" {text}"
                data.append(label)
                data.append(values_text)

            # Get substitutes
            sub_res = query(substitus_file, {"productNumber": routeId})
            if sub_res and sub_res.status_code == 200:
                sub_json = sub_res.json()["data"]["viewer"]["customerById"]
                try:
                    substitutes = sub_json["productByNumber"]["crossSellSubstitutes"][
                        "nodes"
                    ]
                    n = 0
                    sub_index = 17
                    for substitute in substitutes:
                        sub_mfg_name = substitute["summary"]["manufacturer"]["name"]
                        sub_desc = substitute["summary"]["title"]
                        sub_productNumber = substitute["summary"]["productNumber"]
                        sub_sku = substitute["summary"]["sku"]  # same as catNum
                        sub_catNum = substitute["summary"]["catNum"]  # same as catNum
                        sub_upc = substitute["summary"]["upc"]
                        sub_mfg_name = sub_mfg_name.replace(sub_catNum, "").strip()
                        data[sub_index + n] = sub_mfg_name
                        data[sub_index + n + 1] = sub_desc
                        data[sub_index + n + 2] = sub_productNumber
                        n += 3
                except Exception as e:
                    pass  # no substitute
            # Save product to excel
            write_row = (row + (page * page_size)) - 100
            process_excel.writeRow(sheet_obj, write_row, data)
            row += 1

        # Get expired prices
        prices = [p[1] for p in prices_expired]
        price_res = query(prices_file, {"productNumbers": prices})
        cell = 16
        if price_res and price_res.status_code == 200:
            price_json = price_res.json()["data"]["viewer"]["customerById"]
            products = price_json["productsByNumbers"]
            for n in range(len(products)):
                if "amount" in products[n]["prices"][0]["price"]:
                    price = products[n]["prices"][0]["price"]["amount"]
                else:  # call fo price
                    price = products[n]["prices"][0]["price"]["message"]
                row = prices_expired[n][0]
                write_row = (row + (page * page_size)) - 100
                process_excel.writeCell(sheet_obj, write_row, cell, price)

        process_excel.close(wb_obj, file_name)
        log(f"Scraped page {page} from {category_name}")
        saveProgress(category_code, category_name, page)
        # time.sleep(1)  # for not getting killed by vps provider
        if page * page_size < total_count and len(nodes) == page_size:
            getProductsByCategory(category_code, category_name, page + 1, page_size)
        else:
            log(f"Scraped {total_count} products from category {category_name}")
    else:
        log(f"Request failed with status code {response.status_code}")


all_cat = getCategories()
progress = loadProgres()
progress_index = 0
page = 1
if progress:
    category_code, category_name, page = progress
    page = int(page) + 1
    progress_index = all_cat.index([category_code, category_name])
all_cat = all_cat[progress_index:]
for cat in all_cat:
    getProductsByCategory(cat[0], cat[1], page)
    page = 1
