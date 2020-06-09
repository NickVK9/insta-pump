import telebot
from bs4 import BeautifulSoup as bs
import requests as req
import json
from flask import Flask, request
import os
import data_from_instagram
from global_names import TOKEN, HACHTAGS_LIST

TOKEN = TOKEN
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)  # это строка нужна только при запуске на сервере

# КЛАВИАТУРЫ БУДУТ ТУТ
KEYBOARD_TO_ACC = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Сформировать личный кабинет')

KEYBOARD_HASHTAGS = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_TO_ACC.row('Спорт')
KEYBOARD_TO_ACC.row('Бьюти')
KEYBOARD_TO_ACC.row('Охота и рыбалка')
KEYBOARD_TO_ACC.row('Правильно питание')
KEYBOARD_TO_ACC.row('Образование')
KEYBOARD_TO_ACC.row('Бизнес')
KEYBOARD_TO_ACC.row('Медицина и фармацевтика')
KEYBOARD_TO_ACC.row('Наука и техника')
KEYBOARD_TO_ACC.row('Автомобили и мотоциклы')
KEYBOARD_TO_ACC.row('Лайфстайл')


def bio(message):
    if len(message.text) > 650:
        bot.send_message(message.chat.id, 'Увы, длина превышает 650 символов:( \n \
            попробуй написать текст поменьше)')
    else:
        # тут мы будем записывать био в БД
        bot.send_message(message.chat.id, 'Отличное описание! Спасибо!')

def hashtags(message):
    if message.text not in HACHTAGS_LIST:
        bot.send_message(message.chat.id, 'Используй кнопки!')
    else:
        # записываем хештег в таблицу
        bot.send_message(message.chat.id, 'Отличный выбор! Спасибо!')

@bot.message_handler(commands=['start'])
# обрабатывает действия после кнопки start
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, {}! Приятно познакомиться)'.format(message.from_user.username))
    bot.send_message(message.chat.id, 'Я помогу тебе найти единомышленников, которые как и ты хотят \
        пропиарить свой инстаграм и стать популярными блоггерами)\n \
        Для начало нам надо сформировать твой личный кабинет, который \
        ко всему прочему будет являться анкетой, которую будут видеть \
        другие подписчики бота.')
    bot.send_message(message.chat.id, 'Расскажи нам немного о себе!\n \
        Опиши кратко свой блог, какие цели у твоего блога, о чем ты \
        хочешь рассказать людям через свой блог. Ниже будет приведен \
        пример хорошего (на наш взгляд) описания. \n*сделать ограничение на количество символов ~650* ')
    bot.send_message(message.chat.id, '''
        Я веду свой блог для людей которые любят путешествовать, развиваться, изучать иностранные языки и следить за модой.
        Моя цель помогать с изучением иностранных языков и рассказывать о жизни и учебе заграницей.
        Подписчики ценят меня за мою простоту и открытость.
        Они хотят наблюдать за моим прогрессом в изучении языков и мотивировать себя. 
        Также мой блог для тех , кто хочет выглядеть стильно и применять лайфхаки в выборе одежды.
        Моя целевая аудитория это: девушки и парни от 17 до 26 лет
        Студенты , make up артисты, другие блогеры и фрилансеры.'
        ''')
    bot.send_message(message.chat.id, 'Теперь твоя очередь описать себя: ')
    bot.register_next_step_handler(message, bio)
    bot.send_message(message.chat.id, 'Давай теперь определимя с общей тематикой твоего блога! \n \
        По этим хештегам бы будем подбирать тебе единомышленников! \
        Выбери один', reply_markup=KEYBOARD_HASHTAGS)
    bot.register_next_step_handler(message, hashtags)
    bot.send_message(message.chat.id, 'И последниц шаг к формированию личного кабинета!\n \
        Жми кнопку "Сформировать личный кабинет)"', reply_markup=KEYBOARD_TO_ACC)
    


@bot.message_handler(content_types=['text'])
def send_text(message):
    # основная функция, отвечает за действия после нажатия кнопок
    if message.text == 'Сформировать личный кабинет':
        bot.send_message(message.chat.id, 'Введи свой инстаграм логин:')
        bot.register_next_step_handler(message, data_from_instagram.take_info(message.text, friend=0))
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
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

