import json
import process_excel


def scrape_schools():
    with open("acel.json", "r") as f:
        schools_json = json.load(f)

    schools = []
    for school in schools_json:

        # Extract school name and URL
        name = school["SchoolName"]
        address = school["Address"]
        email = school["EMail"]
        schools.append([name, address, email])

    return schools


# Main scraping
file_name = "language.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Education"
schools_list = scrape_schools()
for row in range(len(schools_list)):
    process_excel.writeRow(sheet_obj, row + 2, schools_list[row])

process_excel.close(wb_obj, file_name)
