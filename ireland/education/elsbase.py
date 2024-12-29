import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def scrape_schools():
    url = f"https://www.eslbase.com/schools/ireland"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)

    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    school_items = soup.findAll("div", "schools-grid__item")

    schools = []
    for item in school_items:

        # Extract address
        address = item.find("div", "schools-grid__school").text.split("\n")[0].strip()

        # Extract url
        url_tag = item.find("div", class_="schools-grid__url").find("a")
        url = url_tag.get("href").strip()
        # Extract name
        name = item.text.strip()

        school = [name, url, address]
        print(school)
        schools.append(school)

    return schools


# Main scraping
file_name = "elsbaseLangage.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Education"
school_data = scrape_schools()
for row in range(len(school_data)):
    process_excel.writeRow(sheet_obj, row + 2, school_data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
