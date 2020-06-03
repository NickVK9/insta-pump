def rating_count(user_info):
    followers = user_info['followed_by']
    comments_count = sum([comment['comments'] for comment in user_info['photos_data']])
    comments_percent = comments_count / 12 / followers
    print('Процент комментов', comments_percent)

    likes_count = sum([like['likes'] for like in user_info['photos_data']])
    likes_percent = likes_count / 12 / followers
    print('Процент лайков', likes_percent)

    all_times = [time['time'] for time in user_info['photos_data']]
    periods = []
    for period in all_times:
        try:
            periods.append(period - all_times[all_times.index(period) +1])
        except IndexError:
            break
    mean_time = 1 / sum(periods) / 11 / 60 / 60 / 24
    print('Среднее время между постами:', mean_time)

    rating = followers * (1 + likes_percent * 0.85 + comments_percent * 0.15) * (1 + mean_time)
    print('Рейтинг:', rating)
    return rating



test = {'user_id': 1, 'user_login': 'oohnastya', 'followed_by': 22498, 'subscribed_to': 2604, 'publications': 727, 'business_category': None, 'subcategory': None, 'photos_data': [{'comments': 45, 'time': 1590591363, 'likes': 451}, {'comments': 46, 'time': 1590422705, 'likes': 574}, {'comments': 84, 'time': 1590334339, 'likes': 980}, {'comments': 46, 'time': 1590073478, 'likes': 487}, {'comments': 56, 'time': 1589814193, 'likes': 1020}, {'comments': 61, 'time': 1589468169, 'likes': 787}, {'comments': 41, 'time': 1589208814, 'likes': 733}, {'comments': 55, 'time': 1589120893, 'likes': 550}, {'comments': 93, 'time': 1588609592, 'likes': 616}, {'comments': 65, 'time': 1588169012, 'likes': 563}, {'comments': 61, 'time': 1587913671, 'likes': 812}, {'comments': 41, 'time': 1587567633, 'likes': 546}]}
# поправить id
rating_count(test)