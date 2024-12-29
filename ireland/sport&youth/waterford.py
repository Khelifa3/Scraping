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
    items = soup.find_all("tr")[1:]
    entities = []
    for item in items:
        tds = item.find_all("td")
        # Extract  name
        name = tds[0].text.strip()
        # Extract address and email
        print(name)
        try:
            address = tds[5].find("a")["href"]
        except:
            continue
        email = tds[1].text.strip()
        entity = [name, email, address]
        print(entity)
        entities.append(entity)

    return entities


def scrape_entities():
    url = f"https://www.waterfordsportspartnership.ie/category/club-contacts/"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", "card-body")
    print(len(divs))
    links = [a.find("a", href=True)["href"] for a in divs]
    items = []
    for link in links:
        entities = scrape_link(link)
        items += entities

    return items


# Main scraping
file_name = "waterford.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Sport"
data = scrape_entities()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
