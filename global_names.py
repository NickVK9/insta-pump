'''Все переменные желательно выносить сюда'''

BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
STORIES_UA = 'Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US; en-US; scale=2.00; 828x1792; 190542906) AppleWebKit/605.1.15'
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
# STORIES_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US; en-US; scale=2.00; 828x1792; 190542906)'
# CHROME_WIN_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US; en-US; scale=2.00; 828x1792; 190542906)'
# #'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36'
# #Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36
# #Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36
# #Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15
LOGIN = 'support_me_pls'  # секретные данные акка
PASSWORD = 'ihatemark33'
PHONE_NUMBER = '+380916072406'
# LOGIN = 'instapump_support'  # секретные данные акка
# PASSWORD = 'wetryingtodothisabout1week'
# PHONE_NUMBER = '+79651139899'

TEST_TOKEN = '966681948:AAGh0kkPeXK1CtEsqDAQEjVAFDF6sYuniew'
TOKEN = '1124156274:AAFcflDj26OJnIcucf70mi7IlNdikylfGIw'
DANIIL_TEST_TOKEN = 'ТВОЙ ТОКЕН'

HACHTAGS_LIST = ['Спорт', 'Бьюти', 'Охота и рыбалка', 'Правильно питание', 'Образование' ,'Бизнеc', 'Медицина и фармацевтика', 'Наука и техника', 'Автомобили и мотоциклы', 'Лайфстайл']

# postgres credentials
HOST = 'ec2-54-217-236-206.eu-west-1.compute.amazonaws.com'
DATABASE = 'd2ssbkf4ga9d3o'
USER = 'guvxwdzgxdgawx'
PORT = 5432
PASSWORD = '9ebcc5b7dc6e10c31186138f66c909c23bd6111011ca39def0bec5e0d04aa13f'
URI = 'postgres://guvxwdzgxdgawx:9ebcc5b7dc6e10c31186138f66c909c23bd6111011ca39def0bec5e0d04aa13f@ec2-54-217-236-206.eu-west-1.compute.amazonaws.com:5432/d2ssbkf4ga9d3o'
HEROKU_CLI = 'heroku pg:psql postgresql-trapezoidal-82978 --app instapump'
