import telebot
from bs4 import BeautifulSoup as bs
import requests 
import json
from flask import Flask, request
import os
import data_from_instagram
from global_names import TEST_TOKEN, HACHTAGS_LIST
import time
from InstagramAPI import InstagramAPI

TOKEN = TEST_TOKEN 
bot = telebot.TeleBot(TOKEN)


# КЛАВИАТУРЫ БУДУТ ТУТ
KEYBOARD_TO_ACC = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Сформировать личный кабинет')
KEYBOARD_TO_ACC.row('test')


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

def parse_time(l): #timestamps to mean difference between them in days
	t = 0
	for i in range(len(l) - 1):
		t += (l[i] - l[i+1]) / (len(l) - 1)
	return t / 86400

def search(user): #search procedure
	mean_likes = 0; mean_comments = 0; mean_time = list()
	followers = 0; following = 0; media_count = 0

	api = InstagramAPI('zaribrown37', 'youknowguysblm123')
	api.login()
	api.searchUsername(user)
	result = api.LastJson
	
	followers = result['user']['follower_count'] #getting info from account
	following = result['user']['following_count']
	media_count = result['user']['media_count']
	biography = result['user']['biography']
	category = result['user']['category']

	username_id = result['user']['pk'] # Get user ID
	user_posts = api.getUserFeed(username_id) # Get user feed
	result = api.LastJson 

	for i in range(18): #getting info from last 18 publications
		mean_likes += result['items'][i]['like_count'] / 18
		mean_comments += result['items'][i]['comment_count'] / 18
		mean_time.append(result['items'][i]['taken_at'])
	mean_time = parse_time(mean_time) 

	print('User: ', user) #printing info
	print('Followers: ', followers)
	print('Following: ', following)
	print('Publications count: ', media_count)
	print('Category: ', category)
	print('Mean likes', round(mean_likes, 2))
	print('Mean comments: ', round(mean_comments, 2))
	print('Mean time between publications(days): ', round(mean_time, 3))
	print('Bio: ', biography)	
    
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
        # тут мы будем записывать био в БД
        bot.send_message(message.chat.id, 'Отличное описание! Спасибо!')
        bot.send_message(message.chat.id, '''Давай теперь определимя с общей тематикой твоего блога!
        
По этим хештегам бы будем подбирать тебе единомышленников!
Выбери один: ''', reply_markup=KEYBOARD_HASHTAGS)
        bot.register_next_step_handler(message, hashtags)


def hashtags(message):
    if message.text not in HACHTAGS_LIST:
        bot.send_message(message.chat.id, 'Используй кнопки!')
        bot.send_message(message.chat.id, '''Давай теперь определимя с общей тематикой твоего блога!

По этим хештегам бы будем подбирать тебе единомышленников!
Выбери один: ''', reply_markup=KEYBOARD_HASHTAGS)
        bot.register_next_step_handler(message, hashtags)
    else:
        # записываем хештег в таблицу
        bot.send_message(message.chat.id, 'Отличный выбор! Спасибо!')
        bot.send_message(message.chat.id, '''И последний шаг к формированию личного кабинета!

Жми кнопку "Сформировать личный кабинет)"''', reply_markup=KEYBOARD_TO_ACC)

@bot.message_handler(commands=['start'])
# обрабатывает действия после кнопки start
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, {}! Приятно познакомиться)'.format(message.from_user.username))
    bot.send_message(message.chat.id, '''Я помогу тебе найти единомышленников, которые как и ты хотят пропиарить свой инстаграм и стать популярными блоггерами)

Для начала нам надо сформировать твой личный кабинет, который ко всему прочему будет являться анкетой, которую будут видеть другие подписчики бота.''')
    bot.send_message(message.chat.id, '''Расскажи нам немного о себе!
Опиши кратко свой блог, какие цели у твоего блога, о чем ты
хочешь рассказать людям через свой блог. Ниже будет приведен
пример хорошего (на наш взгляд) описания. \n*сделать ограничение на количество символов ~650* 
        ''')
    time.sleep(3)
    bot.send_message(message.chat.id, '''
Я веду свой блог для людей которые любят путешествовать, развиваться, изучать иностранные языки и следить за модой.
Моя цель помогать с изучением иностранных языков и рассказывать о жизни и учебе заграницей.

Подписчики ценят меня за мою простоту и открытость.
Они хотят наблюдать за моим прогрессом в изучении языков и мотивировать себя.

Также мой блог для тех , кто хочет выглядеть стильно и применять лайфхаки в выборе одежды.
Моя целевая аудитория это: девушки и парни от 17 до 26 лет
Студенты , make up артисты, другие блогеры и фрилансеры.'
        ''')
    time.sleep(5)
    bot.send_message(message.chat.id, 'Теперь твоя очередь описать себя: ')
    bot.register_next_step_handler(message, bio)

@bot.message_handler(content_types=['text'])
def send_text(message):
    # основная функция, отвечает за действия после нажатия кнопок
    if message.text == 'Сформировать личный кабинет':
        bot.send_message(message.chat.id, 'Введи свой инстаграм логин:')
        bot.register_next_step_handler(message, data_from_instagram.take_info)
    elif message.text == 'test':
        bot.send_message(message.chat.id, 'Enter login:')
        bot.register_next_step_handler(message, search)
    else:
        bot.send_message(message.chat.id, 'Используй кнопки!')

# на локалхосте раскоментить
bot.polling()


