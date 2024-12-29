import requests
import json


with open("allcategory.json", "r") as f:
    data = json.load(f)

# Set up the request headers
headers = {
    "Accept": "application/graphql-response+json, application/graphql+json, application/json, text/event-stream, multipart/mixed",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkFGNkQyNDVBNjhBNTIwQzM3MjcyQjA3RTY5MTI5M0U5RjYyQzZDQzhSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6InIyMGtXbWlsSU1OeWNyQi1hUktUNmZZc2JNZyJ9.eyJuYmYiOjE3MzE1MDMwMzAsImV4cCI6MTczMTU3NTAzMCwiaXNzIjoiaHR0cHM6Ly9hdXRoLnJleGVsdXNhLmNvbSIsImF1ZCI6InNmLndlYiIsImNsaWVudF9pZCI6InN0b3JlZnJvbnQtd2ViLXYyIiwic3ViIjoiMjY1NDk5IiwiYXV0aF90aW1lIjoxNzMxNTAxMDMxLCJpZHAiOiJsb2NhbCIsImFjciI6InVucHciLCJ3dWlkIjoia2dhU3pnQUVEUnZBIiwiZGlkIjoiOTlhODQ1M2YtYWNiZi00NjE3LTlkMmYtZjQ3ODkwMjQ0N2Y4IiwianRpIjoiMEU2M0UzQzc0OURBRTUwMzc4RDYyMEQwQTQzNDNEQkYiLCJzaWQiOiI5MkE4NTY0QkVDMzMxODlDMjFGMkRBMTMwNDRBODZCNSIsImlhdCI6MTczMTUwMzAzMCwic2NvcGUiOlsic2Yud2ViIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbInB3ZCJdfQ.hH7kDnOsAVmjJ6TzqxS-haoQvHvimixA5QLRS34o6egRyC_x4iVxyybpWmg9ZpichFmB6DlXzJwdk2BWhFVhz73JFOg9_nAsB_oo5ltCPRoN2brr-SRhotnzSAROg2SOXcAGtI1TZO6uRVbkxsPzAgme7gHntIl4VH1MwKlHSVx1gtR-A4tamETkrbJguL7v6GCJl51CZsjU4dutwFlSYzoSsedOoOAIbbZ28RF8MovxiRJ61n7UGiF9CnxsZK1KDiZC1erPjr1n_nTyo2s496NcyT_rRs0LO0GgumHxv4-T-lCyO3FJSvSK9dECaLKuu5tJTotxU7_Swok1aB64-Q",  # Replace with your actual access token
    "Content-Type": "application/json",
    "Origin": "https://www.rexelusa.com",
    "Priority": "u=1, i",
    "Referer": "https://www.rexelusa.com/s/electrical-boxes-enclosures?cat=r1i4hp",
    "Sec-CH-UA": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Traceparent": "00-5bc4ade7774c0d4d0299f0bf33b5d6b0-5b82d37e38e69833-01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

# API endpoint
url = "https://www.rexelusa.com/graphql"

# Make the POST request
response = requests.post(
    url,
    json=data,
    headers=headers,
)

# Check if the request was successful and output the response data
if response.status_code == 200:
    data = response.json()["data"]["viewer"]["categoriesRoot"]
    nodes = data["nodes"]
    for node in nodes:
        cat_code = node["code"]
        cat_name = node["shortName"]
        children = node["children"]
        product_count = 0
        for child in children:
            product_count += child["descendantProductsCount"]
        print(cat_code, cat_name, product_count)

else:
    print(f"Request failed with status code {response.status_code}")
