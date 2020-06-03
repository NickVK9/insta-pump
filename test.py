import requests

user = 'korepanov_nv'
ask = requests.get('https://www.instagram.com/{}/?__a=1'.format(user))
answer = ask.json()
print(answer)