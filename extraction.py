from InstagramAPI import InstagramAPI
import math
import psycopg2

conn = psycopg2.connect(dbname='postgres', user='postgres', 
                        password='password', 
                        host='localhost',
                        port=5432)

def parse_time(l): #timestamps to mean difference between them in days
	t = 0
	for i in range(len(l) - 1):
		t += (l[i] - l[i+1]) / (len(l) - 1)
	return t / 86400

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

# считает рейтинг каждого юзера
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
                periods.append(period - all_times[all_times.index(period) + 1])
            except IndexError:
                break
        if periods == []:
            mean_time = 0
        else:
            mean_time = 1 / sum(periods) / 11 / 60 / 60 / 24
    except TypeError:
        mean_time = 0
    rating = math.sqrt(((followers ** 2) * ((1 + likes_percent * 0.8 + comments_percent * 0.2) * (1 + mean_time)) ** 2) + (followers ** 2))/1000
    return rating

def search(user): #search procedure
    message = user
    user = user.text
    user = user.lower()
    user = user.strip()
    PERSONAL = '''
💎 Telegram Name : {tg_log}
💎Instagram Name: {inst_log}
🔸Тип профиля: {type}

👥Подписчики : {followers}
❣Среднее кол-во лайков: {mean_like}
📊Рейтинг : {rating}

📝Bio: {bio}
Hashtags : {hashtg}
'''
    mean_likes = 0; mean_comments = 0; mean_time = list()
    followers = 0; following = 0; media_count = 0

    api = InstagramAPI('zaribrown37', 'youknowguysblm123')
    api.login()
    api.searchUsername(user)
    result = api.LastJson
	
    followers = result['user']['follower_count'] #getting info from account
    following = result['user']['following_count']
    try:
        media_count = result['user']['media_count']
    except:
        print("Медиа нет")
    try:
        biography = result['user']['biography']
    except:
        print('Биографии нет')
    try:
        category = result['user']['category']
    except:
        category = 'Не бизнес аккаунт'

    username_id = result['user']['pk'] # Get user ID
    try:
        user_posts = api.getUserFeed(username_id) # Get user feed
        result = api.LastJson
        for i in range(len(result['items'])): #getting info from last 18 publications
            mean_likes += result['items'][i]['like_count'] / len(result['items'])
            mean_comments += result['items'][i]['comment_count'] / len(result['items'])
            mean_time.append(result['items'][i]['taken_at'])
    except:
        mean_likes = 0
        mean_comments = 0
        mean_time = []
    mean_time = parse_time(mean_time) 

    rating = 10 # полставить функцию
    curs = conn.cursor()
    curs.execute('SELECT bio FROM users WHERE tg_id = {}'.format(message.from_user.id))
    bio = curs.fetchone()
    print('Bio', bio)
    bio = bio[0]
    curs.execute('SELECT hashtags FROM users WHERE tg_id = {}'.format(message.from_user.id))
    hashtg = curs.fetchone()
    print('Hash', hashtg)
    hashtg = hashtg[0]
    PERSONAL = PERSONAL.format(
                tg_log=message.from_user.username,
                inst_log=user,
                type=category,
                followers=followers,
                mean_like=round(mean_likes, 2),
                rating=rating,
                bio=bio,
                hashtg=hashtg
            )
    curs.execute('UPDATE users SET inst_log= %s, profile_type= %s, followers= %s, mean_likes= %s, rating= %s WHERE tg_id= %s', (user, category, followers, mean_likes, rating, message.from_user.id))
    conn.commit()
    conn.close()
    return PERSONAL
    '''
	print('User: ', user) #printing info
	print('Followers: ', followers)
	print('Following: ', following)
	print('Publications count: ', media_count)
	print('Category: ', category)
	print('Mean likes', round(mean_likes, 2))
	print('Mean comments: ', round(mean_comments, 2))
	print('Mean time between publications(days): ', round(mean_time, 3))
	print('Bio: ', biography)	
    '''

def friends_rating(user):
    user = user.text
    user = user.lower()
    user = user.strip()
    PERSONAL = """
💎Instagram Name: {inst_log}
🔸Тип профиля: {type}

👥Подписчики : {followers}
❣Среднее кол-во лайков: {mean_like}
📊Рейтинг : {rating}
"""
    api = InstagramAPI('zaribrown37', 'youknowguysblm123')
    api.login()
    api.searchUsername(user)
    result = api.LastJson
    followers = result['user']['follower_count']
    try:
        category = result['user']['category']
    except:
        category = 'Не бизнес аккаунт'
    username_id = result['user']['pk'] # Get user ID
    try:
        user_posts = api.getUserFeed(username_id) # Get user feed
        result = api.LastJson
        for i in range(len(result['items'])): #getting info from last 18 publications
            mean_likes += result['items'][i]['like_count'] / len(result['items'])
            mean_comments += result['items'][i]['comment_count'] / len(result['items'])
            mean_time.append(result['items'][i]['taken_at'])
    except:
        mean_likes = 0
        mean_comments = 0
        mean_time = []
    rating = 10 # посчитать
    PERSONAL = PERSONAL.format(
                inst_log=user,
                type=category,
                followers=followers,
                mean_like=round(mean_likes, 2),
                rating=rating
            )
    '''Может сделать после рейтинга друга кнопку "пригласить друга"'''
    return PERSONAL 