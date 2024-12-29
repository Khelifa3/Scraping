import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# Main scraping
file_name = "childcareonline.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Childcare"


def scrape_schools():
    url = f"https://childcareonline.ie/childcare-directory/"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e, url)
    if response.status_code != 200:
        print(response.status_code, url)
    soup = BeautifulSoup(response.text, "html.parser")
    school_items = soup.find_all("div", "member-row")
    schools = []
    for item in school_items:

        # Extract school name and URL
        school_name_tag = item.find("h3")
        name = school_name_tag.text.strip()

        # Extract address
        address_tag = item.find("div", "col-md-5")
        address = address_tag.text.strip().replace("Location", "")
        address = address.replace("\n\t\t\t\t", " ")
        # Extract email
        try:
            email = re.findall(email_pattern, str(item))[0]
        except:
            continue
        school = [name, email, address]
        print(school)
        row = sheet_obj.max_row + 1
        process_excel.writeRow(sheet_obj, row, school)
        process_excel.save(wb_obj, file_name)


scrape_schools()
process_excel.close(wb_obj, file_name)
