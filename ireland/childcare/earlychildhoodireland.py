import process_excel
import json


def scrape_schools():

    with open("creches.json", "r") as f:
        creches_json = json.load(f)

    creches = []
    for creche in creches_json:
        name = creche["servicename"]
        address = creche["addr1"] + " " + creche["addr2"] + " " + creche["addr3"]
        city = creche["city"]
        country = creche["country"]
        county = creche["county"]
        address += " " + city
        address += " " + county
        address += " " + country
        address = address.strip()
        email = creche["email"]
        creches.append([name, email, address])
        print([name, email, address])

    return creches


# Main scraping
wb_obj, sheet_obj = process_excel.openExcel("post_primary.xlsx")
sheet_obj.title = "Childcare and Early Years Service"
school_data = scrape_schools()
file_name = "creche.xlsx"
for row in range(len(school_data)):
    process_excel.writeRow(sheet_obj, row + 2, school_data[row])
    process_excel.save(wb_obj, file_name)


process_excel.close(wb_obj, file_name)
