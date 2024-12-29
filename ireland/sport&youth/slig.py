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
    print(link)
    name_tag = soup.find("h1")
    name = name_tag.text.strip()
    print(name)
    try:
        address_tag = soup.find_all("div", "iconlist_content")[1]
        address = address_tag.text.strip()
    except:
        address = ""
    email = re.findall(email_pattern, soup.text.strip())[0]
    entity = [name, email, address]
    print(entity)
    return entity


def scrape_entities(page):
    url = f"https://www.sligosportandrecreation.ie/club-directory/page/{page}/?paginate=true"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", "cspml_details_title")
    links = [a.find("a", href=True)["href"] for a in divs]
    items = []
    for link in links:
        entities = scrape_link(link)
        items.append(entities)

    return items


def getPage():
    all_items = []
    for p in range(1, 7):
        all_items += scrape_entities(p)
    return all_items


# Main scraping
file_name = "sligosportandrecreation.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Sport"
data = getPage()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
