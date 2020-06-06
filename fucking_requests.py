import requests
from bs4 import BeautifulSoup

ask = requests.get('https://www.instagram.com/korepanov_nv/?__a=1')
soup = BeautifulSoup(ask.content, 'lxml')
body = soup.find("div", id="bodyContent")

print(body)

# web: python instapump_testbot.py