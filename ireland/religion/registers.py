import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# Main scraping
file_name = "registers.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Relegious"


def makeRequest(url):
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def getEmail(name):
    name = "+".join(name.split(" "))
    url = f"https://www.google.com/search?q=email+{name}"
    response = scraper.get(url)
    print(response.status_code)
    if response.status_code == 429:
        time.sleep(60)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        email = re.findall(email_pattern, soup.text.strip())[0]
    except:
        email = ""
    time.sleep(2)
    return email


def scrape_entities(page):
    url = f"https://registers.nli.ie/ga/parishes?page={page}&q=%2A"
    response = makeRequest(url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", "search_result_document")

    for div in divs:
        # Extract  name
        city = div.find("h5").text.strip()
        diocese = div.find("span", "index-top").text.strip()
        # Extract address and email
        name, county = diocese.split("|")
        name = name.replace("\n    ", "")
        address = f"{name}, {city}, {county}"
        email = getEmail(address)
        entity = [f"{name} {city}", email, address]
        print(entity)

        row = sheet_obj.max_row + 1
        process_excel.writeRow(sheet_obj, row, entity)
        process_excel.save(wb_obj, file_name)
    print(f"Page {page} done")


for p in range(1, 116):
    scrape_entities(p)
process_excel.close(wb_obj, file_name)
