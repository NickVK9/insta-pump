import telebot
from bs4 import BeautifulSoup as bs
import requests as req
import json
from flask import Flask, request
import os
import data_from_instagram
from global_names import HACHTAGS_LIST, DANIIL_TEST_TOKEN

TOKEN = DANIIL_TEST_TOKEN
bot = telebot.TeleBot(TOKEN)


# КЛАВИАТУРЫ БУДУТ ТУТ
KEYBOARD_ANY = telebot.types.ReplyKeyboardMarkup(True)
KEYBOARD_ANY.row('Узнать рейтинг друга')


@bot.message_handler(commands=['start'])
# обрабатывает действия после кнопки start
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, {}'.format(message.from_user.username))

@bot.message_handler(content_types=['text'])
def send_text(message):
    # основная функция, отвечает за действия после нажатия кнопок
    if message.text == 'Узнать рейтинг друга':
        bot.send_message(message.chat.id, 'Введи инстаграм логин друга:')
        bot.register_next_step_handler(message, data_from_instagram.take_info(message, friend=1))
    else:
        pass

# на локалхосте 
bot.polling()


