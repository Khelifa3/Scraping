import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel
import time

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def scrape_schools():
    url = f"https://www.familysupportni.gov.uk/Search/Results?page=1&sTypeID=138&serviceID=153&distance=0&order=4&vacancies=0&specialneeds=0&pickup=0&vouchers=0&flexible=0&funded=0&taxfree=0&breakfast=0&studentPlacements=0"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e, url)
    if response.status_code != 200:
        print(response.status_code, url)
    soup = BeautifulSoup(response.text, "html.parser")
    schools = []

    school_items = soup.find_all("div", "organisation")

    schools = []
    for item in school_items:

        # Extract school name and URL
        school_name_tag = item.find("p", "resultheading")
        name = school_name_tag.text.strip()

        # Extract address
        address_tag = item.find_all("p")[1]
        if address_tag:
            address = address_tag.text.strip()

        # Extract email
        email_tag = item.find("span", {"class": "glyphicon-send"})
        if email_tag:
            email = email_tag.parent.text.strip()
            email = re.findall(email_pattern, email)[0]
        else:
            email = ""
        school = [name, email, address]
        schools.append(school)

    return schools


# Main scraping
file_name = "childminder.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Childcare"
school_data = scrape_schools()
for row in range(len(school_data)):
    process_excel.writeRow(sheet_obj, row + 2, school_data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
