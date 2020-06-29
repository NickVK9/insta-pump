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
from extraction import search, friends_rating
import psycopg2

conn = psycopg2.connect(dbname='postgres', user='postgres', 
                        password='password', 
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
KEYBOARD_MENU.row('Посмотреть рейтинг друга') # DONE
KEYBOARD_MENU.row('Посмотреть других юзеров для коллаборации')
KEYBOARD_MENU.row('Топ юзеров бота') # DONE
KEYBOARD_MENU.row('Посмотреть заявки на рекламу')
KEYBOARD_MENU.row('Мои заявки')
KEYBOARD_MENU.row('Настройки')

KEYBOARD_SETTINGS = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_SETTINGS.row('Сменить описание bio')
KEYBOARD_SETTINGS.row('Сменить hashtag')
KEYBOARD_SETTINGS.row('Вопросы/предложения')
KEYBOARD_SETTINGS.row('Верификация')
KEYBOARD_SETTINGS.row('Вернутся в меню')

KEYBOARD_MY_OR_NOT = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_MY_OR_NOT.row('Только моя', 'Все')

def collab(message):
    if message.text == 'Только моя':
        curs = conn.cursor()
        curs.execute('SELECT hashtags FROM users WHERE tg_id = {}'.format(message.from_user.id))
        hashtag = curs.fetchone()
        hashtag = hashtag[0]
        curs.execute('SELECT inst_log, hashtags, rating FROM users')
    elif message.text == 'Все':
        pass
    else:
        bot.send_message(message.chat.id, 'Используй кнопки', reply_markup=KEYBOARD_MENU)

def friend(message):
    try:
        friend_info = friends_rating(message)
        bot.send_message(message.chat.id, friend_info, reply_markup=KEYBOARD_MENU)
    except KeyError:
        bot.send_message(message.chat.id, 'Юзер не найден, попробуй еще раз', reply_markup=KEYBOARD_MENU)


def bio(message):
    if len(message.text) > 650:
        bot.send_message(message.chat.id, '''Увы, длина превышает 650 символов:(
Попробуй написать текст поменьше)''')
        bot.send_message(message.chat.id, 'Теперь твоя очередь описать себя: ')
        bot.register_next_step_handler(message, bio)
    elif len(message.text) < 50:
        bot.send_message(message.chat.id, 'Попробуй рассказать о себе побольше!')
        bot.send_message(message.chat.id, 'Теперь твоя очередь описать себя: ')
        bot.register_next_step_handler(message, bio)
    else:
        curs = conn.cursor()
        curs.execute('UPDATE users SET bio= %s WHERE tg_id= %s', (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, 'Отличное описание! Спасибо!')
        bot.send_message(message.chat.id, '''Давай теперь определимя с общей тематикой твоего блога!
По этим хештегам бы будем подбирать тебе единомышленников!
Выбери один: ''', reply_markup=KEYBOARD_HASHTAGS)
        bot.register_next_step_handler(message, hashtags)

def personal_account(message):
    try:
        reply = search(message)
        bot.send_message(message.chat.id, reply)
        bot.send_message(message.chat.id, 'Поздравляем! Вы зарегистрировались, воспользуйтесь меню для управления ботом', reply_markup=KEYBOARD_MENU)
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
        curs.execute('UPDATE users SET hashtags= %s WHERE tg_id= %s', (message.text, message.from_user.id))
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
        bot.send_message(message.chat.id, 'Если ты блогер, то этот бот поможет тебе устраивать коллаборации с другими блогерами, а также находить рекламодателей')
        bot.send_message(message.chat.id, 'Выбери с помощью кнопок меню, для чего ты здесь: ', reply_markup=KEYBOARD_WHO_AM_I)
    except:
        bot.send_message(message.chat.id, 'Кажется, у тебя уже есть аккаунт, воспользуйся меню', reply_markup=KEYBOARD_MENU)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Я хочу найти блогера для рекламы':
        bot.send_message(message.chat.id, 'Введи свой инстаграм логин:')
        bot.register_next_step_handler(message, bio)
    elif message.text == 'Посмотреть рейтинг друга':
        bot.send_message(message.chat.id, 'Введи инстаграм логин друга:')
        bot.register_next_step_handler(message, friend)
    elif message.text == 'Я блогер':
        bot.send_message(message.chat.id,'Тогда давай зарегистрируемся')
        bot.send_message(message.chat.id, '''Расскажи нам немного о себе!
Опиши кратко свой блог, какие цели у твоего блога, о чем ты
хочешь рассказать людям через свой блог. Ниже будет приведен
пример хорошего (на наш взгляд) описания.
Напиши от 50 до 600 символов 
        ''')
        bot.register_next_step_handler(message, bio)
    elif message.text == 'Топ юзеров бота':
        curs = conn.cursor()
        curs.execute("SELECT * FROM users ORDER BY rating DESC LIMIT 10")
        top = curs.fetchall()
        log1, log2, log3, log4, log5, log6, log7, log8, log9, log10 = top[0][2], top[1][2], top[2][2], top[3][2], top[4][2], top[5][2], top[6][2], top[7][2], top[8][2], top[9][2]
        tg_log1, tg_log2, tg_log3, tg_log4, tg_log5, tg_log6, tg_log7, tg_log8, tg_log9, tg_log10 = top[0][3], top[1][3], top[2][3], top[3][3], top[4][3], top[5][3], top[6][3], top[7][3], top[8][3], top[9][3]
        mean1, mean2, mean3, mean4, mean5, mean6, mean7, mean8, mean9, mean10 = top[0][5], top[1][5], top[2][5], top[3][5], top[4][5], top[5][5], top[6][5], top[7][5], top[8][5], top[9][5]
        rat1, rat2, rat3, rat4, rat5, rat6, rat7, rat8, rat9, rat10 = top[0][6], top[1][6], top[2][6], top[3][6], top[4][6], top[5][6], top[6][6], top[7][6], top[8][6], top[9][6]
        followers1, followers2, followers3, followers4, followers5, followers6, followers7, followers8, followers9, followers10 = top[0][10], top[1][10], top[2][10], top[3][10], top[4][10], top[5][10], top[6][10], top[7][10], top[8][10], top[9][10]
        info = """
1. {log1}, {tg_log1}, {mean1}, {rat1}, {followers1}
2. {log2}, {tg_log2}, {mean2}, {rat2}, {followers2}
3. {log3}, {tg_log3}, {mean3}, {rat3}, {followers3}
4. {log4}, {tg_log4}, {mean4}, {rat4}, {followers4}
5. {log5}, {tg_log5}, {mean5}, {rat5}, {followers5}
6. {log6}, {tg_log6}, {mean6}, {rat6}, {followers6}
7. {log7}, {tg_log7}, {mean7}, {rat7}, {followers7}
8. {log8}, {tg_log8}, {mean8}, {rat8}, {followers8}
9. {log9}, {tg_log9}, {mean9}, {rat9}, {followers9}
10.{log10}, {tg_log10}, {mean10}, {rat10}, {followers10}
        """.format(
            log1=log1, log2=log2, log3=log3, log4=log4, log5=log5, log6=log6, log7=log7, log8=log8, log9=log9, log10=log10,
            tg_log1=tg_log1, tg_log2=tg_log2, tg_log3=tg_log3, tg_log4=tg_log4, tg_log5=tg_log5, tg_log6=tg_log6, tg_log7=tg_log7, tg_log8=tg_log8, tg_log9=tg_log9, tg_log10=tg_log10,
            mean1=mean1, mean2=mean2, mean3=mean3, mean4=mean4, mean5=mean5, mean6=mean6, mean7=mean7, mean8=mean8, mean9=mean9, mean10=mean10,
            rat1=rat1, rat2=rat2, rat3=rat3, rat4=rat4, rat5=rat5, rat6=rat6, rat7=rat7, rat8=rat8, rat9=rat9, rat10=rat10,
            followers1=followers1, followers2=followers2, followers3=followers3, followers4=followers4, followers5=followers5, followers6=followers6, followers7=followers7, followers8=followers8, followers9=followers9, followers10=followers10
        )
        bot.send_message(message.chat.id, info, reply_markup=KEYBOARD_MENU)
    elif message.text == 'Посмотреть других юзеров для коллаборации':
        bot.send_message(message.chat.id, 'Искать блоггеров в вашей категории или во всех?', reply_markup=KEYBOARD_MY_OR_NOT)
        bot.register_next_step_handler(message, collab)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, используй клавиатуру', reply_markup=KEYBOARD_MENU)

bot.polling()