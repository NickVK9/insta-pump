import requests

ask = requests.get('https://www.instagram.com/korepanov_nv/?__a=1')
answer = ask.json()
print(answer)

# web: python instapump_testbot.py