import requests
import csv
import time

def take_info(user):
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
                # комменты, время, лайки
                photos.append(edge['node']['edge_media_to_comment']['count'])
                photos.append(edge['node']['taken_at_timestamp'])
                photos.append(edge['node']['edge_liked_by']['count'])
        needed = [user_id, user, followed_by, edge_follow, content_count, business_category, category_enum]
        if photos != None:
        	needed.extend(photos)
        return needed

if __name__ == "__main__":
	user_id = 0
	users_before = []
	users = [['User_id','Name', 'Followers', 'Following', 'Photos_count', 'Business_category', 'Subcategory', 'Photos1_count', 'Photos1_time', 'Photos1_likes' \
	'Photos2_count', 'Photos2_time', 'Photos2_likes', 'Photos3_count', 'Photos3_time', 'Photos3_likes', 'Photos4_count', 'Photos4_time', 'Photos4_likes', \
	'Photos5_count', 'Photos5_time', 'Photos5_likes', 'Photos6_count', 'Photos6_time', 'Photos6_likes', 'Photos7_count', 'Photos7_time', 'Photos7_likes', \
	'Photos8_count', 'Photos8_time', 'Photos8_likes', 'Photos9_count', 'Photos9_time', 'Photos9_likes', 'Photos10_count', 'Photos10_time', 'Photos10_likes', \
	'Photos11_count', 'Photos11_time', 'Photos11_likes', 'Photos12_count', 'Photos12_time', 'Photos12_likes']]
	with open('users_for_test.txt', 'r', encoding="utf8") as file:
		for line in file:
			a = line.split('\n')
			a = a[0]
			users_before.append(a)

	for i in users_before:
		s1 = time.time()
		users.append(take_info(i))
		user_id += 1
		s2 = time.time()
		print('Готово за: ', s2-s1, 'Осталось', 174-user_id)
	FILENAME = 'users2.csv'
	with open(FILENAME, "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerows(users)



''' Tests
print(take_info('m_s_nobody'))
print(take_info('korepanov_nv'))
print(take_info('anzhelika_sty'))
print(take_info('vkmfbmfbmblfvvfvfdvbdfbgngngngnggnrvv'))
'''