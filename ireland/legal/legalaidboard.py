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


def decodeEmail(string):
    r = int(string[:2], 16)
    email = "".join(
        [chr(int(string[i : i + 2], 16) ^ r) for i in range(2, len(string), 2)]
    )
    return email


def scrape_link(link):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")
    list_b = soup.find_all("b")
    for b in list_b:
        b.name = "strong"
        print(b, b.next_sibling)
    content = soup.find("div", "content")
    entities_tag = content.find_all("p")
    for entity_tag in entities_tag:
        # Extract  name
        try:
            name = entity_tag.find("strong").text.strip()
        except Exception as e:
            pass
        # print(name)
        # Extract address and email
        address_tag = entity_tag.text.strip().replace(name, "").split("Tel")[0]
        address = address_tag.strip()
        # address = " ".join(address.split())
        # print(address)
        email = re.findall(email_pattern, entity_tag.text.strip())
        # print(email)
        entity = [name, email, address]
        # print(entity)

    return entity


def scrape_entities(page):
    url = f"https://www.legalaidboard.ie/en/contact-us/find-a-law-centre/"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")
    div = soup.find("div", "content")
    links = [a["href"] for a in div.find_all("a", href=True)]
    items = []
    for link in links:
        entities = scrape_link(f"https://www.legalaidboard.ie{link}")
        items += entities

    return items


def getAllPages():
    all_data = []
    for p in range(1, 20):
        data = scrape_entities(p)
        all_data += data

    return all_data


# Main scraping
file_name = "legalaidboard.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Legal"
data = getAllPages()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
