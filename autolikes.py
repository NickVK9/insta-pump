import telebot
from bs4 import BeautifulSoup as bs
import requests 
import json
from flask import Flask, request
import os
from global_names import *
from InstagramAPI import InstagramAPI
from time import sleep
import random
import psycopg2


TOKEN = TOKEN
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)

KEYBOARD_START = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_START.row('Да!', 'Конечно!')

# api = InstagramAPI('zaribrown37', 'youknowguysblm123')

def target_acc(message):
    data = message.text
    trg = data.strip()
    main_func(message, trg) 


def auth(message):
    data = message.text
    data = data.split(':')
    if len(data) > 1:
        login = data[0].strip()
        password = data[1].strip()
        conn = psycopg2.connect(dbname=DATABASE, user=USER, 
                                    password=PASSWORD, 
                                    host=HOST,
                                    port=PORT)
        curs = conn.cursor()
        curs.execute('UPDATE target SET login= %s, password= %s WHERE tg_id= %s', (login, password, message.from_user.id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, 'Введи имя таргет аккаунта, из которого будут перетекать подписчики')
        bot.register_next_step_handler(message, target_acc)
    else:
        bot.send_message(message.chat.id, 'Неверный формат, попробуешь еще раз?', reply_markup=KEYBOARD_START)


@bot.message_handler(commands=['start'])
def start_message(message):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, 
                                    password=PASSWORD, 
                                    host=HOST,
                                    port=PORT)
    curs = conn.cursor()
    curs.execute("INSERT INTO target(tg_id) VALUES (%s)" % message.from_user.id)
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, 'Бот для привлечения на твой аккаунт целевой аудитории')
    bot.send_message(message.chat.id, 'Вы предоставляете боту данные своего аккаунта.\nОн под вашим аккаунтом лайкает активных подписчиков ваших конкурентов.\nПодписчики заходят на ваш аккаунт и видит интересную для себя информацию и подписывается на вас.')
    bot.send_message(message.chat.id, 'Мы не храним данные вашего аккаунта.\nКаждый раз, когда бот запускается, он запрашивает ваш логин и пароль и передает их в программу и удаляет.\nВаши данные передаются в зашифрованном виде.')
    bot.send_message(message.chat.id, 'Готов прокачать свой аккаунт?', reply_markup=KEYBOARD_START)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Да!' or message.text == 'Конечно!':
        bot.send_message(message.chat.id, 'Поехали!')
        bot.send_message(message.chat.id, 'Введи свой инстаграм логин и пароль в таком виде\nlogin:password')
        bot.register_next_step_handler(message, auth)

'''Убедитесь, что аккаунт таргет открыт'''

def get_likes_list(username, api):
    users_list = []
    api.searchUsername(username)
    result = api.LastJson
    username_id = result['user']['pk'] # Get user ID
    api.getUserFeed(username_id) # Get user feed
    result = api.LastJson
    media_id = result['items'][0]['id'] # Get most recent post
    api.getMediaLikers(media_id) # Get users who liked
    users = api.LastJson['users']
    for user in users: # Push users to list
        users_list.append({'pk':user['pk'], 'username':user['username'], 'privat':user['is_private']})
    return users_list


def like(message, users_list, api):
    users_list = users_list[:5]
    counter = 0
    counter2 = 0 
    for user in users_list:
        if counter == 20:
            counter2 += 1
            bot.send_message(message.chat.id, 'Лайкнул 20, осталось: {}'.format(len(users_list)-(20*counter2)))
            counter = 0
            print('Лайкнул 20, осталось: {}'.format(len(users_list)-(20*counter2)))
        print('засыпаю')
        sleep(random.randint(20, 40))
        print('отоспался')
        print('проверяю на приват')
        print(user)
        if user['is_private'] == False:
            print('не приватный, беру айди')
            user_id = user['pk']
            print('беру публикации')
            api.getUserFeed(user_id)
            print('публикашки взял')
            try:
                user_media_id = api.LastJson['items'][0]['pk']
                api.like(user_media_id)
                print('LIKED 1')
                user_media_id2 = api.LastJson['items'][1]['pk']
                api.like(user_media_id2)
                print('LIKED 2')
                counter += 1
            except IndexError:
                print('Нет фото')
        else:
            print('Private account')
    bot.send_message(message.chat.id, 'Готово! Жди волну подписчиков!')
    
    


def main_func(message,trg):
    try:
        conn = psycopg2.connect(dbname=DATABASE, user=USER, 
                                    password=PASSWORD, 
                                    host=HOST,
                                    port=PORT)
        curs = conn.cursor()
        curs.execute('SELECT login, password FROM target WHERE tg_id = {}'.format(message.from_user.id))
        lp = curs.fetchall()
        conn.close()
        login = lp[0][0]
        password = lp[0][1]
        api = InstagramAPI(login, password)
        api.login()
        try:
            users_list = get_likes_list(trg, api)
        except:
            bot.send_message(message.chat.id, 'Неверный логин таргет аккаунта, попробуешь еще раз?', reply_markup=KEYBOARD_START)
        like(message, users_list, api)
    except:
        bot.send_message(message.chat.id, 'Неверные данные, попробуешь еще раз?', reply_markup=KEYBOARD_START)
    

@server.route('/'+TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://instapump.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))