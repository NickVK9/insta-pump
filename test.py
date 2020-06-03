import requests

reply = requests.get('https://www.instagram.com/korepanov_nv/followers/?__a=1')
print(reply.text)
answer = reply.json()
print(answer)