# Importing Key Libraries
from bs4 import BeautifulSoup
import requests

base_url = 'https://www.dubizzle.com.eg/en/mobile-phones-tablets-accessories-numbers/mobile-phones/'
page = requests.get(base_url)

print(page.text)