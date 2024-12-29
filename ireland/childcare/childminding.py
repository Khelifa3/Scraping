import json
import process_excel


file_name = "childminding.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "childminding"
row = sheet_obj.max_row + 1
# process_excel.writeRow(sheet_obj, row, entity)
# process_excel.save(wb_obj, file_name)

json_file = "carlow"
with open(json_file, "r", encoding="utf-8") as f:
    all_json = json.load(f)
    for a in all_json:
        listing_str = a["listing"]
        listing_json = json.loads(listing_str)
        contacts = listing_json["contacts"]
        for c in contacts:
            first_name = c["FirstName"]
            last_name = c["LastName"]
            name = f"{first_name} {last_name}"
            try:
                email = c["Email"]
            except:
                continue
            street = c["MailingStreet"]
            city = c["MailingCity"]
            state = c["MailingState"]
            try:
                postal_code = c["MailingPostalCode"]
            except:
                postal_code = ""
            address = f"{street}, {city}, {state}, {postal_code}"
            entity = [name, email, address]
            row = sheet_obj.max_row + 1
            process_excel.writeRow(sheet_obj, row, entity)
            process_excel.save(wb_obj, file_name)

process_excel.close(wb_obj, file_name)
