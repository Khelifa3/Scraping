import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# Main scraping
file_name = "goodfirms.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Transport"


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


def scrape_link(link):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")
    # Extract  name
    name = soup.find("div", "profile-name-tagline").text.strip()
    # Extract address and email
    email = ""  # getEmail(name)
    address = soup.find("div", "profile-location-address").text.strip()
    website = soup.find("a", "visit-website")["href"]
    entity = [name, email, address, website]
    print(entity)

    row = sheet_obj.max_row + 1
    process_excel.writeRow(sheet_obj, row, entity)
    process_excel.save(wb_obj, file_name)


def scrape_entities(page):
    url = f"https://www.goodfirms.co/supply-chain-logistics-companies/ireland"
    response = makeRequest(url)

    soup = BeautifulSoup(response.text, "html.parser")
    links = [a["href"] for a in soup.find_all("a", "visit-profile")]
    print(len(links))
    for link in links:
        scrape_link(link)


for p in range(1, 3):
    scrape_entities(p)
process_excel.close(wb_obj, file_name)
