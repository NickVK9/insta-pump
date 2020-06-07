import requests
import json
from bs4 import BeautifulSoup as bs

BASE_URL = 'https://www.instagram.com/'
STORIES_UA = 'Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'

LOGIN = 'instapump_support' # секретные данные акка
PASSWORD = 'wetryingtodothisabout1week'
PHONE_NUMBER = '+79651139899'

session = requests.Session()
session.headers = {'user-agent': CHROME_WIN_UA}

authenticated = False
logged_in = False
rhx_gis = ""
cookies = None

def authenticate_with_login(user):
    """Logs in to instagram."""
    session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
    req = session.get(BASE_URL)

    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

    login_data = {'username': LOGIN, 'password': PASSWORD}
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    login_text = json.loads(login.text)

    if login_text.get('authenticated') and login.status_code == 200:
        session.headers.update({'user-agent': CHROME_WIN_UA})
        print('Удачно залогинился')
        print('Пробую взять инфу')
        ask = session.get(BASE_URL+user)
        soup = bs(ask.text, 'html.parser')
        body = soup.find('body')
        script = body.find('script', text = lambda t: t.startswith('window._sharedData'))

        page_json = script.text.split(' = ', 1)[1].rstrip(';')
        data_json = json.loads(page_json)
        print('Успешно спарсил')
        print('')
        print(data_json)
    else:
        print('Login failed for ' + LOGIN)
