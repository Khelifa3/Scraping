import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# Main scraping
file_name = "goldenpagesTourism.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Tourism"


def makeRequest(url):
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def scrapeLink(url):
    response = makeRequest(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Extract school name and URL
    name = soup.find("h1", "company_name").text.strip()
    name = name.split("\n")[0]

    # Extract address
    address = soup.find("p", "company_address").text.strip()

    # Extract email
    try:
        email = soup.find("a", {"data-event-name": "EmailClick"}).text.strip()
    except:
        return
    school = [name, email, address]
    print(school)
    row = sheet_obj.max_row + 1
    process_excel.writeRow(sheet_obj, row, school)
    process_excel.save(wb_obj, file_name)


def scrape_schools(page):
    url = f"https://www.goldenpages.ie/q/business/advanced/what/Tourist+%26+Heritage+Attractions/{page}"
    response = makeRequest(url)
    soup = BeautifulSoup(response.text, "html.parser")
    school_items = soup.find_all("a", "listing_title_link")
    print(len(school_items))
    links = [a["href"] for a in school_items]
    for link in links:
        scrapeLink(f"https://www.goldenpages.ie{link}")
    print(f"Scraped page {page}")


for p in range(1, 12):
    scrape_schools(p)
    process_excel.close(wb_obj, file_name)
