from bs4 import BeautifulSoup as bs
import requests as req
import json

URL = 'https://www.instagram.com/{}'

def scrape_data(user):
	ask = req.get(URL.format(user))

	soup = bs(ask.text, 'html.parser')
	body = soup.find('body')
	script = body.find('script', text = lambda t: t.startswith('window._sharedData'))

	page_json = script.text.split(' = ', 1)[1].rstrip(';')
	data_json = json.loads(page_json)

	return data_json

if __name__ == '__main__':
	username = str(input())
	data = scrape_data(username)
	print(data)
