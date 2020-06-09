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
KEYBOARD_ANY.row('ТУТ ВПИСЫВАЕТСЯ СТРОКА КЛАВИАТУРЫ')


@bot.message_handler(commands=['start'])
# обрабатывает действия после кнопки start
def start_message(message):
    bot.send_message(message.chat.id, '*SOMETHING')

@bot.message_handler(content_types=['text'])
def send_text(message):
    # основная функция, отвечает за действия после нажатия кнопок
    if message.text == '*SOMETHING*':
        pass
    else:
        pass

# на локалхосте 
bot.polling()


