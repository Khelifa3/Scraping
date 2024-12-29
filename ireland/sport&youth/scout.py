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


def scrape_entities(page):
    url = f"https://www.scouts.ie/find-a-scout-group-in-ireland?5e565be3_page={page}"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", "w-dyn-item")
    print(len(divs))
    entities = []
    for div in divs:

        # Extract  name
        try:
            name = div.find("h4", "group-grid").text.strip()
            print(name)
        except Exception as e:
            print(e)
            continue
        # Extract address and email
        address = div.find("div", "address").text.strip()
        try:
            email = re.findall(email_pattern, div.text.strip())[0]
        except:
            email = ""
        entity = [name, email, address]
        print(entity)
        entities.append(entity)

    return entities


def getAllPages():
    items = []
    for p in range(1, 18):
        items += scrape_entities(p)
    return items


# Main scraping
file_name = "scouts.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Sport"
data = getAllPages()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
