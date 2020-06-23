import telebot
from bs4 import BeautifulSoup as bs
import requests 
import json
from flask import Flask, request
import os
import data_from_instagram
from global_names import *
import time
import re
from InstagramAPI import InstagramAPI
from extraction import search
import psycopg2

conn = psycopg2.connect(dbname='postgres', user='postgres', 
                        password='simplyclever343', 
                        host='localhost',
                        port=5432)

TOKEN = TEST_TOKEN
bot = telebot.TeleBot(TOKEN)

#server = Flask(__name__)  # это строка нужна только при запуске на сервере

# КЛАВИАТУРЫ БУДУТ ТУТ
KEYBOARD_TO_ACC = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Сформировать личный кабинет')

KEYBOARD_HASHTAGS = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_HASHTAGS.row('Спорт')
KEYBOARD_HASHTAGS.row('Бьюти')
KEYBOARD_HASHTAGS.row('Охота и рыбалка')
KEYBOARD_HASHTAGS.row('Правильно питание')
KEYBOARD_HASHTAGS.row('Образование')
KEYBOARD_HASHTAGS.row('Бизнес')
KEYBOARD_HASHTAGS.row('Медицина и фармацевтика')
KEYBOARD_HASHTAGS.row('Наука и техника')
KEYBOARD_HASHTAGS.row('Автомобили и мотоциклы')
KEYBOARD_HASHTAGS.row('Лайфстайл')

KEYBOARD_WHO_AM_I = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_WHO_AM_I.row('Я блогер')
KEYBOARD_WHO_AM_I.row('Я хочу найти блогера для рекламы')

KEYBOARD_MENU = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_MENU.row('Доработка')

def bio(message):
    if len(message.text) > 650:
        bot.send_message(message.chat.id, '''Увы, длина превышает 650 символов:(
Попробуй написать текст поменьше)''')
        bot.send_message(message.chat.id, 'Теперь твоя очередь описать себя: ')
        bot.register_next_step_handler(message, bio)
    elif len(message.text) < 100:
        bot.send_message(message.chat.id, 'Попробуй рассказать о себе побольше!')
        bot.send_message(message.chat.id, 'Теперь твоя очередь описать себя: ')
        bot.register_next_step_handler(message, bio)
    else:
        curs = conn.cursor()
        curs.execute("INSERT INTO users(bio) VALUES (%s) WHERE tg_id = {}".format(message.from_user.id), (message.text))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, 'Отличное описание! Спасибо!')
        bot.send_message(message.chat.id, '''Давай теперь определимя с общей тематикой твоего блога!
По этим хештегам бы будем подбирать тебе единомышленников!
Выбери один: ''', reply_markup=KEYBOARD_HASHTAGS)
        bot.register_next_step_handler(message, hashtags)

def personal_account(message):
    try:
        reply = search(message)
        bot.send_message(message.chat.id, reply)
        bot.send_message(message.chat.id, 'Поздравляем! Вы зарегистрировались, воспользуйтесь еню для управления ботом', reply_markup=KEYBOARD_MENU)
    except KeyError:
        bot.send_message(message.chat.id, 'Такого пользователя мы не нашли, попробуй еще раз: ')
        bot.register_next_step_handler(message, personal_account)

def hashtags(message):
    if message.text not in HACHTAGS_LIST:
        bot.send_message(message.chat.id, 'Используй кнопки!')
        bot.send_message(message.chat.id, '''Давай теперь определимя с общей тематикой твоего блога!

По этим хештегам бы будем подбирать тебе единомышленников!
Выбери один: ''', reply_markup=KEYBOARD_HASHTAGS)
        bot.register_next_step_handler(message, hashtags)
    else:
        curs = conn.cursor()
        curs.execute("INSERT INTO users(hashtags) VALUES (%s) WHERE tg_id = {}".format(message.from_user.id), (message.text))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, 'Отличный выбор! Спасибо!')
        bot.send_message(message.chat.id, '''И последний шаг к формированию личного кабинета!
        Напиши пожалуйста свой инстаграм логин, мы сформируем твой личный кабинет''')
        bot.register_next_step_handler(message, personal_account)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, {}! Приятно познакомиться)'.format(message.from_user.username))
    try:
        curs = conn.cursor()
        curs.execute("INSERT INTO users(tg_id, tg_log) VALUES (%s, %s)", (message.from_user.id, message.from_user.username))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, 'Если ты блогер, то этот бот поможет тебе устраивать коллаборации с другими блогерами, а также находить рекламодателей')
        bot.send_message(message.chat.id, 'Выбери с помощью кнопок меню, для чего ты здесь: ', reply_markup=KEYBOARD_WHO_AM_I)
    except:
        bot.send_message(message.chat.id, 'Кажется, у тебя уже есть аккаунт, воспользуйся меню', reply_markup=KEYBOARD_MENU)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Я блогер':
        bot.send_message(message.chat.id, 'Введи свой инстаграм логин:')
        bot.register_next_step_handler(message, personal_account)
    elif message.text == 'Я хочу найти блогера для рекламы':
        bot.send_message(message.chat.id,'Тогда давай зарегестрируемся')
        bot.send_message(message.chat.id, '''Расскажи нам немного о себе!
        Опиши кратко свой блог, какие цели у твоего блога, о чем ты
        хочешь рассказать людям через свой блог. Ниже будет приведен
        пример хорошего (на наш взгляд) описания.
        Напиши от 50 до 600 символов 
        ''')
        bot.register_next_step_handler(message, bio)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, используй клавиатуру', reply_markup=KEYBOARD_WHO_AM_I)

bot.polling()