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
        print(e, url)
        return None
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def scrape_link(link):
    response = makeRequest(link)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", "club")
    entities = []
    for item in items:

        # Extract  name
        name_tag = item.find("h4")
        if name_tag == None:
            continue
        name = name_tag.text.strip()
        # Extract address and email
        info_tag = item.find_all("p")

        email = re.findall(email_pattern, item.text.strip())
        if len(email) > 0:
            email = email[0]
        else:
            continue

        print(info_tag)
        address = info_tag[1].text.strip().replace("Tel", "")
        entity = [name, email, address]
        print(entity)
        entities.append(entity)

    return entities


def scrape_entities():
    url = "http://www.cavansportspartnership.ie/default.aspx?StructureID_str=6"
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
    if response.status_code != 200:
        print(response.status_code, url)

    soup = BeautifulSoup(response.text, "html.parser")

    dir_div = soup.find("div", "clubdir")
    links = dir_div.find_all("a", href=True)
    links = [link["href"] for link in links]
    items = []
    for link in links:
        print(link)
        entities = scrape_link(link)
        items += entities

    return items


# Main scraping
file_name = "cavana.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Sports"
data = scrape_entities()
for row in range(len(data)):
    process_excel.writeRow(sheet_obj, row + 2, data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
