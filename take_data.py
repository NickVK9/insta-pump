import requests
import csv
import time

def check_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения функции {} равно {} секунд'.format(func, end - start), end='\n\n')
        return (result)
    return wrapper

@check_time
def rating_count(user_info):
    followers = user_info['followed_by']
    try:
        comments_count = sum([comment['comments'] for comment in user_info['photos_data']]) 
        comments_percent = comments_count / 12 / followers 
        print('Процент комментов', comments_percent)
    except TypeError:
        comments_percent = 0
        print('Процент комментов', comments_percent)

    try:
        likes_count = sum([like['likes'] for like in user_info['photos_data']])
        likes_percent = likes_count / 12 / followers
        print('Процент лайков', likes_percent)
    except TypeError:
        likes_percent = 0
        print('Процент лайков', likes_percent)
    try:   
        all_times = [time['time'] for time in user_info['photos_data']]
        periods = []
        for period in all_times:
            try:
                periods.append(period - all_times[all_times.index(period) +1])
            except IndexError:
                break
        if periods == []:
            mean_time = 0
        else:
            mean_time = 1 / sum(periods) / 11 / 60 / 60 / 24
        print('Среднее время между постами:', mean_time)
    except TypeError:
        mean_time = 0
        print('Среднее время между постами:', mean_time)
    rating = followers * (1 + likes_percent * 0.85 + comments_percent * 0.15) * (1 + mean_time)
    print('Рейтинг:', rating)
    return rating

@check_time
def take_info(user):
    user_id = 1
    ask = requests.get('https://www.instagram.com/{}/?__a=1'.format(user))
    answer = ask.json()
    if answer == {}: # ввел несуществующего пользователя
        return None
    else:
        followed_by = answer['graphql']['user']['edge_followed_by']['count'] # количество подписчиков
        edge_follow = answer['graphql']['user']['edge_follow']['count'] # количество подписок
        content_count = answer['graphql']['user']['edge_owner_to_timeline_media']['count'] # количество публикаций в акке
        if answer['graphql']['user']['is_business_account']: # проверка, является ли акк бизнес
            business_category = answer['graphql']['user']['business_category_name'] # категория бизнеса
            category_enum = answer['graphql']['user']['category_enum'] # конкретная категория
        else:
            business_category = None
            category_enum = None
        if answer['graphql']['user']['is_private']: # если аккаунт закрытый
            photos = None
        else:
            photos = []
            for edge in answer['graphql']['user']['edge_owner_to_timeline_media']['edges']:
                data = {
                    'comments':edge['node']['edge_media_to_comment']['count'],
                    'time':edge['node']['taken_at_timestamp'],
                    'likes':edge['node']['edge_liked_by']['count']
                        }
                # комменты, время, лайки 
                photos.append(data)
        needed = {
            'user_id':user_id, 'user_login':user, 
            'followed_by':followed_by, 'subscribed_to':edge_follow, 
            'publications':content_count, 'business_category':business_category, 
            'subcategory':category_enum, 'photos_data':photos
        }
        user_id += 1
        return needed

if __name__ == "__main__":
    user_id = 1
    users_before = []
    users = [['Юзер id','Логин', 'Подписчиков', 'Подписок', 'Кол-во фото', 'Бизнес категория', 'Подкатегория', 'Данные по фото']]
    with open('users_for_test.txt', 'r', encoding="utf8") as file:
        for line in file:
            a = line.split('\n')
            a = a[0]
            users_before.append(a)
    
    for i in users_before:
        s1 = time.time()
        info = take_info(i)
        rating = rating_count(info)
        result = {user_id:rating}
        users.append(result)
        user_id += 1
        s2 = time.time()
        to_end = s2 - s1
        print('Готово за: ', to_end, 'Осталось: ', len(users_before)-user_id)

    print(users)
    
    FILENAME = 'users.csv'
    with open(FILENAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(users)

''' Tests
print(take_info('m_s_nobody'))
print(take_info('korepanov_nv'))
print(take_info('anzhelika_sty'))
print(take_info('vkmfbmfbmblfvvfvfdvbdfbgngngngnggnrvv'))
'''