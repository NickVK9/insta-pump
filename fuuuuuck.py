import telebot
from bs4 import BeautifulSoup as bs
import requests as req
import json
from flask import Flask, request
import os

def scrape_data(user):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    ask = req.get('https://www.instagram.com/{}'.format(user))
    print(ask.headers)
    print('')
    print(ask.history)
    print('')
    print(ask.cookies)

    soup = bs(ask.text, 'html.parser')
    body = soup.find('body')
    script = body.find('script', text = lambda t: t.startswith('window._sharedData'))

    page_json = script.text.split(' = ', 1)[1].rstrip(';')
    data_json = json.loads(page_json)
    print('')
    print(data_json)


    return data_json

scrape_data('korepanov_nv')