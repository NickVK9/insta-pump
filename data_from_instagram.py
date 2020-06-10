import telebot
from bs4 import BeautifulSoup as bs
import requests # as req
import json
from flask import Flask, request
import os
from global_names import *
import math
from database import FakeOrm

#session = req.Session()
#session.headers = {'user-agent': CHROME_WIN_UA}

# если запуск на тестовом боте, то TEST_TOKEN, иначе TOKEN
TOKEN = TOKEN
bot = telebot.TeleBot(TOKEN)

KEYBOARD_TO_ACC = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Сформировать личный кабинет')
KEYBOARD_TO_ACC.row('Узнать рейтинг друга')


# парсит сраный html
def authenticate_with_login(user):
    """Logs in to instagram."""
    session = requests.Session()
    '''
    session.headers = {'user-agent': CHROME_WIN_UA}
    session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
    req = session.get(BASE_URL)

    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

    login_data = {'username': LOGIN, 'password': PASSWORD}
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    login_text = json.loads(login.text)
    print(login_text)
    '''
    session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
    req = session.get(BASE_URL)

    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

    session.headers.update({'user-agent': CHROME_WIN_UA})
    autication = True
    if autication == True:#login_text.get('authenticated') and login.status_code == 200:
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
        #print('Код ответа: ', login.status_code)
    return data_json


# фиксирует нужное количество знаков после запятой
def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


# считает рейтинг каждого юзера
def rating_count(user_info):
    followers = user_info['followed_by']
    try:
        comments_count = sum([comment['comments'] for comment in user_info['photos_data']])
        comments_percent = comments_count / 12 / followers
    except TypeError:
        comments_percent = 0

    try:
        likes_count = sum([like['likes'] for like in user_info['photos_data']])
        likes_percent = likes_count / 12 / followers
    except TypeError:
        likes_percent = 0
    try:
        all_times = [time['time'] for time in user_info['photos_data']]
        periods = []
        for period in all_times:
            try:
                periods.append(period - all_times[all_times.index(period) + 1])
            except IndexError:
                break
        if periods == []:
            mean_time = 0
        else:
            mean_time = 1 / sum(periods) / 11 / 60 / 60 / 24
    except TypeError:
        mean_time = 0
    rating = math.sqrt(((followers ** 2) * ((1 + likes_percent * 0.8 + comments_percent * 0.2) * (1 + mean_time)) ** 2) + (followers ** 2))/1000
    return rating


# главная функция, собирает вю инфу и вставляет в личный кабинет
def take_info(user):
    PERSONAL = '''
💎 Telegram Name : {tg_log}
💎Instagram Name: {inst_log}
🔸Тип профиля: {type}

👥Подписчики : {followers}
❣Среднее кол-во лайков: {mean_like}
📊Рейтинг : {rating}

📝Bio: *В РАЗРАБОТКЕ*
Hashtags : *В РАЗРАБОТКЕ*

Одобрен *В РАЗРАБОТКЕ*
'''
#📨Реферальная ссылка: *В РАЗРАБОТКЕ*
    database_connecter = FakeOrm()
    message = user
    user = user.text
    database_connecter.tg_id = message.from_user.id
    database_connecter.tg_log = message.from_user.username
    database_connecter.inst_log = user
    user_id = 1
    answer = authenticate_with_login(user)
    if answer == {}:  # ввел несуществующего пользователя
        bot.send_message(message.chat.id, 'Такого пользователя не существует, попробуйте еще раз', reply_markup=KEYBOARD_TO_ACC)
        return None
    else:
        try:
            followed_by = answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']  # количество подписчиков
            edge_follow = answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']  # количество подписок
            content_count = answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']  # количество публикаций в акке
            if answer['entry_data']['ProfilePage'][0]['graphql']['user']['is_business_account']:  # проверка, является ли акк бизнес
                business_category = answer['entry_data']['ProfilePage'][0]['graphql']['user']['business_category_name']  # категория бизнеса
                category_enum = answer['entry_data']['ProfilePage'][0]['graphql']['user']['category_enum']  # конкретная категория
            else:
                business_category = None
                category_enum = None
            if answer['entry_data']['ProfilePage'][0]['graphql']['user']['is_private']:  # если аккаунт закрытый
                photos = None
            else:
                photos = []
                for edge in answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
                    data = {
                        'comments':edge['node']['edge_media_to_comment']['count'],
                        'time':edge['node']['taken_at_timestamp'],
                        'likes':edge['node']['edge_liked_by']['count']
                            }
                    # комменты, время, лайки 
                    photos.append(data)
            needed = {
                'user_id':user_id, 'user_login':user, 
                'followed_by':followed_by, 'subscribed_to':edge_follow, 
                'publications':content_count, 'business_category':business_category, 
                'subcategory':category_enum, 'photos_data':photos
            }
            user_id += 1
            rating = rating_count(needed)
            needed['user_rating'] = rating
            likes_count = sum([like['likes'] for like in needed['photos_data']])
            mean_like = likes_count / 12
            database_connecter.profile_type = needed['subcategory']
            database_connecter.followers = needed['followed_by']
            database_connecter.mean_likes = int(mean_like)
            database_connecter.rating = toFixed(needed['user_rating'], 4)
            PERSONAL = PERSONAL.format(
                tg_log=message.from_user.username,
                inst_log=user,
                type=needed['subcategory'],
                followers=needed['followed_by'],
                mean_like=int(mean_like),
                rating=toFixed(needed['user_rating'], 4)
            )
            database_connecter.telegram_insert()
            bot.send_message(message.chat.id, PERSONAL, reply_markup=KEYBOARD_TO_ACC)
        except KeyError:
            bot.send_message(message.chat.id, 'Вы ввели несуществующий аккаунт', reply_markup=KEYBOARD_TO_ACC)


def friends_rating(user):
    PERSONAL = '''
💎Instagram Name: {inst_log}
🔸Тип профиля: {type}

👥Подписчики : {followers}
❣Среднее кол-во лайков: {mean_like}
📊Рейтинг : {rating}
        '''
    message = user
    user = user.text
    user_id = 1
    answer = authenticate_with_login(user)
    if answer == {}:  # ввел несуществующего пользователя
        bot.send_message(message.chat.id, 'Такого пользователя не существует, попробуйте еще раз', reply_markup=KEYBOARD_TO_ACC)
        return None
    else:
        try:
            followed_by = answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']  # количество подписчиков
            edge_follow = answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']  # количество подписок
            content_count = answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']  # количество публикаций в акке
            if answer['entry_data']['ProfilePage'][0]['graphql']['user']['is_business_account']:  # проверка, является ли акк бизнес
                business_category = answer['entry_data']['ProfilePage'][0]['graphql']['user']['business_category_name']  # категория бизнеса
                category_enum = answer['entry_data']['ProfilePage'][0]['graphql']['user']['category_enum']  # конкретная категория
            else:
                business_category = None
                category_enum = None
            if answer['entry_data']['ProfilePage'][0]['graphql']['user']['is_private']:  # если аккаунт закрытый
                photos = None
            else:
                photos = []
                for edge in answer['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
                    data = {
                        'comments':edge['node']['edge_media_to_comment']['count'],
                        'time':edge['node']['taken_at_timestamp'],
                        'likes':edge['node']['edge_liked_by']['count']
                            }
                    # комменты, время, лайки 
                    photos.append(data)
            needed = {
                'user_id':user_id, 'user_login':user, 
                'followed_by':followed_by, 'subscribed_to':edge_follow, 
                'publications':content_count, 'business_category':business_category, 
                'subcategory':category_enum, 'photos_data':photos
            }
            user_id += 1
            rating = rating_count(needed)
            needed['user_rating'] = rating
            likes_count = sum([like['likes'] for like in needed['photos_data']])
            mean_like = likes_count / 12
            PERSONAL = PERSONAL.format(
                inst_log=user,
                type=needed['subcategory'],
                followers=needed['followed_by'],
                mean_like=int(mean_like),
                rating=toFixed(needed['user_rating'], 4)
            )
            bot.send_message(message.chat.id, PERSONAL, reply_markup=KEYBOARD_TO_ACC)
        except KeyError:
            bot.send_message(message.chat.id, 'Такого аккаунта не существует', reply_markup=KEYBOARD_TO_ACC)
