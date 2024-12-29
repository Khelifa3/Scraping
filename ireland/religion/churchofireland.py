import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# Main scraping
file_name = "churchofireland.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Relegious"


def makeRequest(url):
    try:
        r = scraper.get("https://www.churchofireland.org/")
        print(r.status_code)
        response = scraper.get(url)
    except Exception as e:
        print(e)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def scrape_entities(page):
    url = f"https://www.churchofireland.org/directory/search?query=%&page={page}"
    response = makeRequest(url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("li")
    print(len(divs))

    for div in divs:
        # Extract  name
        name = div.find("a")
        if not name:
            continue
        name = name.text.strip()
        # Extract address and email
        address = div.find("p", "name").text.strip().replace("\n", " ")
        email = ""
        entity = [name, email, address]
        print(entity)

        row = sheet_obj.max_row
        process_excel.writeRow(sheet_obj, row, entity)
        process_excel.save(wb_obj, file_name)


scrape_entities(1)
process_excel.close(wb_obj, file_name)
