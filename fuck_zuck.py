import telebot
from bs4 import BeautifulSoup as bs
import requests # as req
import json
from flask import Flask, request
import os
from global_names import *
import math
from database import FakeOrm


TOKEN = TOKEN
bot = telebot.TeleBot(TOKEN)

KEYBOARD_TO_ACC = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Сформировать личный кабинет')
KEYBOARD_TO_ACC.row('Узнать рейтинг друга')


# парсит сраный html
def authenticate_with_login(user):
    """Logs in to instagram."""
    session = requests.Session()
    session.headers = {'user-agent': CHROME_WIN_UA}
    session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
    req = session.get(BASE_URL)
    
    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
    
    login_data = {'username': LOGIN, 'password': PASSWORD}
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    print(login.cookies)
    login_text = json.loads(login.text)
    print(login_text)
    
    if login_text.get('authenticated') and login.status_code == 200:
        session.headers.update({'user-agent': CHROME_WIN_UA})
        print('Удачно залогинился')
        print('Пробую взять инфу')
        ask = session.get(BASE_URL+user)
        soup = bs(ask.text, 'html.parser')
        body = soup.find('body')
        script = body.find('script', text=lambda t: t.startswith('window._sharedData'))

        page_json = script.text.split(' = ', 1)[1].rstrip(';')
        data_json = json.loads(page_json)
        print('Успешно спарсил')
    else:
        print('Login failed for ' + LOGIN)
        print('Код ответа: ', login.status_code)
    try:
        return data_json
    except Exception as e:
        bot.send_message(141061019, str(e), reply_markup=KEYBOARD_TO_ACC)