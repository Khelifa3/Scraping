import cloudscraper
import process_excel

scraper = cloudscraper.create_scraper()
file_name = "arcgis.xlsx"
wb_obj, sheet_obj = process_excel.openExcel(file_name)
sheet_obj.title = "Sports"


def makeRequest(url):
    try:
        response = scraper.get(url)
    except Exception as e:
        print(e)
        input(".......")
        makeRequest(url)
    if response.status_code != 200:
        print(response.status_code, url)
    return response


def getObject(object_id):
    url = f"https://services-eu1.arcgis.com/CltcWyRoZmdwaB7T/arcgis/rest/services/GetIrelandActiveAllData/FeatureServer/0/query?f=json&objectIds={object_id}&orderByFields=Name%20ASC&outFields=*&spatialRel=esriSpatialRelIntersects&where=1%3D1"
    response = makeRequest(url)
    entities = response.json()["features"]
    for entity in entities:
        try:
            name = entity["attributes"]["Name"]
            address = entity["attributes"]["Address"].replace("\n", ", ")
            email = entity["attributes"]["Email"]
        except:
            continue
        if email == "":
            continue
        data = [name, email, address]
        row = sheet_obj.max_row + 1
        process_excel.writeRow(sheet_obj, row, data)
        process_excel.save(wb_obj, file_name)
        print(object_id, data)


def getAllObjectId():
    url = "https://services-eu1.arcgis.com/CltcWyRoZmdwaB7T/arcgis/rest/services/GetIrelandActiveAllData/FeatureServer/0/query?f=json&cacheHint=true&maxRecordCountFactor=4&resultOffset=8000&resultRecordCount=8000&where=1%3D1&orderByFields=OBJECTID&outFields=OBJECTID%2CRecordType&outSR=102100&spatialRel=esriSpatialRelIntersects"
    response = makeRequest(url)
    entities = response.json()["features"]
    for entity in entities:
        OBJECTID = entity["attributes"]["OBJECTID"]
        RecordType = entity["attributes"]["RecordType"]
        getObject(OBJECTID)


getAllObjectId()
process_excel.close(wb_obj, file_name)
