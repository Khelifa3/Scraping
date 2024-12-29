import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
from unicodedata import normalize

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


def scrape_link(link, name):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")
    entities = []
    try:
        email = re.findall(email_pattern, soup.text.strip())[0]
    except:
        email = ""
    try:
        address = (
            soup.text.strip()
            .split("Location:")[1]
            .split("Phone")[0]
            .replace("\n", ", ")
        )
    except:
        address = ""
    address = "".join([c for c in address if ord(c) < 128])
    address = address.strip()
    entity = [name, email, address]
    print(entity)

    return entity


def scrape_entities():
    url = f"http://www.uniqueirishhostels.com/http:__www.uniqueirishhostels.com/List_of_Unique_Ireland_Hostels.html"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    hostels = [
        a for a in soup.find_all("a", href=True) if not a["href"].startswith("Unique")
    ]
    print(len(hostels))
    items = []
    for link in hostels:
        entities = scrape_link(
            f"http://www.uniqueirishhostels.com/http:__www.uniqueirishhostels.com/{link['href']}",
            link.text,
        )
        items.append(entities)

    return items


# Main scraping
file_name = "Transport and hostpitality.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Transport and hostpitality"
data = scrape_entities()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
