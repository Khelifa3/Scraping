import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

file_name = "iftn.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Arts"


def makeRequest(url):
    try:
        response = scraper.get(url)
        if response.status_code != 200:
            print(response.status_code, url)
        return response
    except Exception as e:
        print(e, url)
        input("retry...")
    return makeRequest(url)


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
    name_tag = soup.find("div", {"align": "left"})
    name = name_tag.text.strip()
    # Extract address and email
    address_tag = soup.find("div", {"style": "line-height:18px; margin-left:10px"})
    address = address_tag.text.strip().split("\r")[0]
    try:
        email = re.findall(email_pattern, address_tag.text.strip())[0]
    except:
        email = ""
    entity = [name, email, address]
    print(entity)
    row = sheet_obj.max_row
    process_excel.writeRow(sheet_obj, row + 1, entity)
    process_excel.save(wb_obj, file_name)
    return entity


def scrape_page(url):
    response = makeRequest(url)
    soup = BeautifulSoup(response.text, "html.parser")
    print(url)
    links = [
        a["href"] for a in soup.find_all("a", {"style": "color: #0D1556"}, href=True)
    ]
    print(len(links))
    items = []
    for link in links:
        link = f"{url}{link}"
        entities = scrape_link(link)
        items.append(entities)
    return items


def scrape_entities():
    url = f"http://www.iftn.ie/production/production_companies/"
    response = makeRequest(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith("../../production/production_companies/production_sub/")
    ]
    items = []
    for link in links[6:]:
        link = f"{url}{link.split('companies/')[1]}"
        entities = scrape_page(link)
        items += entities

    return items


# Main scraping
data = scrape_entities()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
process_excel.close(wb_obj, file_name)
