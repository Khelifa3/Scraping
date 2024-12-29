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


def scrape_link(link):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("tr")
    entities = []
    for item in items:
        # Extract  name
        name_tag = item.find("td", "item-title")
        if name_tag == None:
            continue
        name = name_tag.text.strip()
        # Extract address and email
        address = name.split(" ")[0]
        if len(address) < 4:
            address = name.split(" ")[0] + " " + name.split(" ")[1]

        address += ", Cork"
        email = item.find_all("td")[4].text.strip()
        entity = [name, email, address]
        print(entity)
        entities.append(entity)

    return entities


def scrape_entities():
    url = f"https://www.corkathletics.org/clubs.html?start="
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    links = [f"{url}{u}" for u in range(0, 61, 20)]
    items = []
    for link in links:
        entities = scrape_link(link)
        items += entities

    return items


# Main scraping
file_name = "corkathletic.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Sport"
data = scrape_entities()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
