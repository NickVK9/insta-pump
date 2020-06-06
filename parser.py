from bs4 import BeautifulSoup as bs
import requests as req

URL = 'https://www.instagram.com/{}'

def parse_data(page):
	data = {}
	page = page.split('-')[0].split()

	data['Followers'] = page[0]
	data['Following'] = page[2]
	data['Posts'] = page[4]

	return data

def scrape_data(user):
	ask = req.get(URL.format(user))
	soup = bs(ask.text, 'html.parser')

	meta = soup.find('meta', property='og:description')

	return parse_data(meta.attrs['content'])

if __name__ == '__main__':
	username = str(input())
	data = scrape_data(username)
	print(data)