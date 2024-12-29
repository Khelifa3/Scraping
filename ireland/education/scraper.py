import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def scrape_schools(page):
    url = f"https://www.gov.ie/en/directory/category/495b8a-schools/?school_roll_number=&school_level=POST+PRIMARY&page={page}"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
        time.sleep(10)
        scrape_schools(page)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
        time.sleep(60)
        scrape_schools(page)
    soup = BeautifulSoup(response.text, "html.parser")
    schools = []

    div = soup.find("div", "reboot-content")
    try:
        school_list = div.find("ul", {"reboot-site-list": ""})
    except Exception as e:
        print(e, url)
        return []
    school_items = school_list.find_all("li")

    schools = []
    for item in school_items:

        # Extract school name and URL
        school_name_tag = item.find("a")
        name = school_name_tag.text.strip()

        # Extract address
        address_tag = item.find("span", {"class": "glyphicon-map-marker"})
        if address_tag:
            address = address_tag.parent.text.strip()
            address = address.replace("\n", "")
            address = " ".join(address.split())

        # Extract email
        email_tag = item.find("span", {"class": "glyphicon-send"})
        if email_tag:
            email = email_tag.parent.text.strip()
            email = re.findall(email_pattern, email)[0]
        school = [name, email, address]
        schools.append(school)

    return schools


# Main scraping
wb_obj, sheet_obj = process_excel.openExcel("post_primary.xlsx")
sheet_obj.title = "Education"
for p in range(1, 74):
    school_data = scrape_schools(p)
    for row in range(len(school_data)):
        process_excel.writeRow(sheet_obj, (p * 10) + (row + 1), school_data[row])
        process_excel.save(wb_obj, "post_primary.xlsx")
    time.sleep(1)


process_excel.close(wb_obj, "sample.xlsx")
