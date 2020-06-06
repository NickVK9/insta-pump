import telebot
from bs4 import BeautifulSoup as bs
import requests as req
import json
from flask import Flask, request
import os

TOKEN = '1124156274:AAFcflDj26OJnIcucf70mi7IlNdikylfGIw' 
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__) # это строка нужна только при запуске на сервере

# КЛАВИАТУРЫ БУДУТ ТУТ
KEYBOARD_TO_ACC = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Сформировать личный кабинет')

# парсит сраный html
def scrape_data(user):
	ask = req.get('https://www.instagram.com/{}'.format(user))

	soup = bs(ask.text, 'html.parser')
	body = soup.find('body')
	script = body.find('script', text = lambda t: t.startswith('window._sharedData'))

	page_json = script.text.split(' = ', 1)[1].rstrip(';')
	data_json = json.loads(page_json)

	return data_json

# установить количество знаков после запятой
def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

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
                periods.append(period - all_times[all_times.index(period) +1])
            except IndexError:
                break
        if periods == []:
            mean_time = 0
        else:
            mean_time = 1 / sum(periods) / 11 / 60 / 60 / 24
    except TypeError:
        mean_time = 0
    rating = followers * (1 + likes_percent * 0.85 + comments_percent * 0.15) * (1 + mean_time)
    return rating

def take_info(user):
    PERSONAL = '''
💎 Telegram Name : {tg_log}
💎Instagram Name: {inst_log}
🔸Тип профиля: {type}

👥Подписчики : {followers}
❣Среднее кол-во лайков: {mean_like}
📊Рейтинг : {rating}

📨Реферальная ссылка: *В РАЗРАБОТКЕ*
📝Bio: *В РАЗРАБОТКЕ*
Hashtags : *В РАЗРАБОТКЕ*

Одобрен *В РАЗРАБОТКЕ*
'''
    message = user
    user = user.text
    user_id = 1
    answer = scrape_data(user)
    if answer == {}: # ввел несуществующего пользователя
        bot.send_message(message.chat.id, 'Такого пользователя не существует, попробуйте еще раз', reply_markup=KEYBOARD_TO_ACC)
        return None
    else:
        followed_by = answer['graphql']['user']['edge_followed_by']['count'] # количество подписчиков
        edge_follow = answer['graphql']['user']['edge_follow']['count'] # количество подписок
        content_count = answer['graphql']['user']['edge_owner_to_timeline_media']['count'] # количество публикаций в акке
        if answer['graphql']['user']['is_business_account']: # проверка, является ли акк бизнес
            business_category = answer['graphql']['user']['business_category_name'] # категория бизнеса
            category_enum = answer['graphql']['user']['category_enum'] # конкретная категория
        else:
            business_category = None
            category_enum = None
        if answer['graphql']['user']['is_private']: # если аккаунт закрытый
            photos = None
        else:
            photos = []
            for edge in answer['graphql']['user']['edge_owner_to_timeline_media']['edges']:
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
            tg_log=message.from_user.username,
            inst_log=user,
            type=needed['subcategory'],
            followers=needed['followed_by'],
            mean_like=int(mean_like),
            rating=toFixed(needed['user_rating'], 4)
        )
        bot.send_message(message.chat.id, PERSONAL, reply_markup=KEYBOARD_TO_ACC)

@bot.message_handler(commands=['start'])
# обрабатывает действия после кнопки start
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, {}! Приятно познакомиться)'.format(message.from_user.username), reply_markup=KEYBOARD_TO_ACC)

@bot.message_handler(content_types=['text'])
def send_text(message):
    # основная функция, отвечает за действия после нажатия кнопок
    if message.text == 'Сформировать личный кабинет':
        bot.send_message(message.chat.id, 'Введи свой инстаграм логин:')
        bot.register_next_step_handler(message, take_info)
    else:
        bot.send_message(message.chat.id, 'Используй кнопки!')

# на локалхосте раскоментить
#bot.polling()

# на локалхосте закомментить, это для работы на сервере
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
    # создаю несколько потоков, так как heroku не дает запускать несколько фалов на сервере одновременно
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

