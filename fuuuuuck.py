from bs4 import BeautifulSoup
import requests

ask = requests.get('https://www.instagram.com/korepanov_nv/')
print(ask.content)
soup = BeautifulSoup(ask.content, 'html.parser')