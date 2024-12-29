import cloudscraper
from bs4 import BeautifulSoup
import re

email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

scraper = cloudscraper.create_scraper()
url = "https://www.google.com/search?q=email+Sn+Cholmcille%2C+Ceathr%C3%BA+Thaidhg"
response = scraper.get(url)
print(response.status_code)
soup = BeautifulSoup(response.text, "html.parser")
email = re.findall(email_pattern, soup.text.strip())[0]
print(email)
