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
    items = soup.find_all("div", "panel-grid-cell")
    entities = []
    for item in items:

        # Extract  name
        name_tag = item.find("h6")
        if name_tag == None:
            continue
        name = name_tag.text.strip()
        # Extract address and email
        address_tag = item.find("p")
        if address_tag == None:
            continue
        address_list = address_tag.text.split("<br>")
        email = re.findall(email_pattern, item.text.strip())
        if len(email) > 0:
            email = email[0]
        else:
            email = [e for e in address_list if "mail" in e]
            if len(email) > 0:
                email = email[0].split(":")[1].split('"')[0]
            else:
                email = ""

        address = address_list[0].split("Phone")[0].replace("\n", "")
        entity = [name, email, address]
        print(entity)
        entities.append(entity)

    return entities


def scrape_entities():
    url = f"https://retirementservices.ie/home-care-providers-ireland/"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")

    links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith("https://retirementservices.ie/home-care-")
    ]
    items = []
    for link in links:
        entities = scrape_link(link)
        items += entities

    return items


# Main scraping
file_name = "homecare2.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Healthcare"
data = scrape_entities()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
