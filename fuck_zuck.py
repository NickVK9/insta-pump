from InstagramAPI import InstagramAPI

LOGIN = 'support_me_pls'  # секретные данные акка
PASSWORD = 'ihatemark33'

api = InstagramAPI(LOGIN, PASSWORD)

users_list = []


def get_likes_list(username):
    api.login()
    api.searchUsername(username)
    result = api.LastJson
    username_id = result['user']['pk'] # Get user ID
    user_posts = api.getUserFeed(username_id) # Get user feed
    result = api.LastJson
    media_id = result['items'][0]['id'] # Get most recent post
    api.getMediaLikers(media_id) # Get users who liked
    users = api.LastJson['users']
    for user in users: # Push users to list
        users_list.append({'pk':user['pk'], 'username':user['username']})
get_likes_list('korepanov_nv')
print(users_list)
