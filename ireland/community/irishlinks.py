import cloudscraper
from bs4 import BeautifulSoup
import re
import process_excel

scraper = cloudscraper.create_scraper()
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

file_name = "irishlinks.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Community and Voluntary Sector"


def makeRequest(url):
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def decodeEmail(string):
    r = int(string[:2], 16)
    email = "".join(
        [chr(int(string[i : i + 2], 16) ^ r) for i in range(2, len(string), 2)]
    )
    return email


def scrape_link(link):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract  name
    name_tag = soup.find("span", "field--name-title")
    name = name_tag.text.strip()
    # Extract address and email
    try:
        general_tag = soup.find("div", "full__container-item-text")
        address_tag = general_tag.find("p")
        address = address_tag.text.strip().replace("\n", ", ").replace(",,", ",")
        div = soup.find("div", "full__container")
        email = re.findall(email_pattern, div.text.strip())[0]
    except:
        return
    entity = [name, email, address]
    print(entity)
    row = sheet_obj.max_row + 1
    process_excel.writeRow(sheet_obj, row, entity)
    process_excel.save(wb_obj, file_name)


def scrape_entities(page):
    url = f"https://www.activelink.ie/irish-links?page={page}/"
    base_url = "https://www.activelink.ie"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", "views-row")
    print(len(divs))
    for div in divs:
        title = div.find("h2")
        link = title.find("a")["href"]
        scrape_link(f"{base_url}{link}")
    print(f"Scraped page {page}")


for p in range(1, 38):
    scrape_entities(p)


process_excel.close(wb_obj, file_name)
