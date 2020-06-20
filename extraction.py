from InstagramAPI import InstagramAPI

def parse_time(l): #timestamps to mean difference between them in days
	t = 0
	for i in range(len(l) - 1):
		t += (l[i] - l[i+1]) / (len(l) - 1)
	return t / 86400

def search(user): #search procedure
	mean_likes = 0; mean_comments = 0; mean_time = list()
	followers = 0; following = 0; media_count = 0

	api = InstagramAPI('zaribrown37', 'youknowguysblm123')
	api.login()
	api.searchUsername(user)
	result = api.LastJson
	
	followers = result['user']['follower_count'] #getting info from account
	following = result['user']['following_count']
	media_count = result['user']['media_count']
	biography = result['user']['biography']
	category = result['user']['category']

	username_id = result['user']['pk'] # Get user ID
	user_posts = api.getUserFeed(username_id) # Get user feed
	result = api.LastJson 

	for i in range(18): #getting info from last 18 publications
		mean_likes += result['items'][i]['like_count'] / 18
		mean_comments += result['items'][i]['comment_count'] / 18
		mean_time.append(result['items'][i]['taken_at'])
	mean_time = parse_time(mean_time) 

	print('User: ', user) #printing info
	print('Followers: ', followers)
	print('Following: ', following)
	print('Publications count: ', media_count)
	print('Category: ', category)
	print('Mean likes', round(mean_likes, 2))
	print('Mean comments: ', round(mean_comments, 2))
	print('Mean time between publications(days): ', round(mean_time, 3))
	print('Bio: ', biography)	

user = input()
search(user)
