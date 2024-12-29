import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def makeRequest(url):
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def decodeEmail(string):
    r = int(string[:2], 16)
    email = "".join(
        [chr(int(string[i : i + 2], 16) ^ r) for i in range(2, len(string), 2)]
    )
    return email


def scrape_link(link):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract  name
    name_tag = soup.find("h1", "com-title")
    name = name_tag.text.strip()
    # Extract address and email
    address_tag = soup.find("div", {"id": "info-column1"})
    address = address_tag.text.strip().replace("Address:", "")
    address = " ".join(address.split())
    email_tag = soup.find("div", {"id": "info-column2"})
    cf_email_span = email_tag.find("span", class_="__cf_email__")
    try:
        data_cfemail = cf_email_span.get("data-cfemail")
        email = decodeEmail(data_cfemail)
    except:
        email = ""
    entity = [name, email, address]
    print(entity)

    return entity


def scrape_entities(page):
    url = f"https://mediastreet.ie/directory/en/businesses/filter-category/event-management/page/{page}/"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")

    links = [a["href"] for a in soup.find_all("a", "read-more-listing", href=True)]
    items = []
    for link in links:
        entities = scrape_link(link)
        items.append(entities)

    return items


def getAllPages():
    all_data = []
    for p in range(1, 20):
        data = scrape_entities(p)
        all_data += data

    return all_data


# Main scraping
file_name = "mediastreet.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Arts"
data = getAllPages()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
