import requests
import json
import time
import sys

BASE_URL = 'https://www.instagram.com/'
STORIES_UA = 'Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
USER_URL = BASE_URL + '{0}/?__a=1'

RETRY_DELAY = 5
CONNECT_TIMEOUT = 90
MAX_RETRIES = 5
MAX_RETRY_DELAY = 60

LOGIN = 'instapump_support'
PASSWORD = 'wetryingtodothisabout1week'
PHONE_NUMBER = '+79651139899'

session = requests.Session()
session.headers = {'user-agent': CHROME_WIN_UA}

authenticated = False
logged_in = False
rhx_gis = ""
cookies = None
class PartialContentException(Exception):
    pass
def authenticate_with_login():
    """Logs in to instagram."""
    session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
    req = session.get(BASE_URL)

    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

    login_data = {'username': LOGIN, 'password': PASSWORD}
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    cookies = login.cookies
    login_text = json.loads(login.text)

    if login_text.get('authenticated') and login.status_code == 200:
        authenticated = True
        logged_in = True
        session.headers.update({'user-agent': CHROME_WIN_UA})
        rhx_gis = ""
    else:
        print('Login failed for ' + LOGIN)

        if 'checkpoint_url' in login_text:
            checkpoint_url = login_text.get('checkpoint_url')
            print('Please verify your account at ' + BASE_URL[0:-1] + checkpoint_url)
        '''
            if self.interactive is True:
                self.login_challenge(checkpoint_url)
        elif 'errors' in login_text:
            for count, error in enumerate(login_text['errors'].get('error')):
                count += 1
                self.logger.debug('Session error %(count)s: "%(error)s"' % locals())
        else:
            self.logger.error(json.dumps(login_text))
        '''
def authenticate_as_guest():
    """Authenticate as a guest/non-signed in user"""
    session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
    req = session.get(BASE_URL)

    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

    session.headers.update({'user-agent': CHROME_WIN_UA})
    rhx_gis = ""
    authenticated = True

def get_profile_info(username):
    url = USER_URL.format(username)
    if logged_in:
        resp = get_json(url)
    else:
        print('Авторизируюсь')
        authenticate_with_login()
        print('Авторизовался')
        resp = get_json(url)
    if resp is None:
        print('Error getting user info for {0}'.format(username))
        return

    

    user_info = json.loads(resp)['graphql']['user']
    try:
        profile_info = {
            'biography': user_info['biography'],
                'followers_count': user_info['edge_followed_by']['count'],
                'following_count': user_info['edge_follow']['count'],
                'full_name': user_info['full_name'],
                'id': user_info['id'],
                'is_business_account': user_info['is_business_account'],
                'is_joined_recently': user_info['is_joined_recently'],
                'is_private': user_info['is_private'],
                'posts_count': user_info['edge_owner_to_timeline_media']['count'],
                'profile_pic_url': user_info['profile_pic_url']
            }
        print(profile_info)
    except (KeyError, IndexError, StopIteration):
        print('Failed to build {0} profile info'.format(username))
        return
def sleep(secs):
    min_delay = 1
    for _ in range(secs // min_delay):
        time.sleep(min_delay)
        if quit:
            return
    time.sleep(secs % min_delay)

def _retry_prompt(url, exception_message):
    """Show prompt and return True: retry, False: ignore, None: abort"""
    answer = input( 'Repeated error {0}\n(A)bort, (I)gnore, (R)etry or retry (F)orever?'.format(exception_message) )
    if answer:
        answer = answer[0].upper()
        if answer == 'I':
            print( 'The user has chosen to ignore {0}'.format(url) )
            return False
        elif answer == 'R':
            return True
        elif answer == 'F':
            print( 'The user has chosen to retry forever' )
            global MAX_RETRIES
            MAX_RETRIES = sys.maxsize
            return True
        else:
            print( 'The user has chosen to abort' )
            return None

def safe_get(*args, **kwargs):
        # out of the box solution
        # session.mount('https://', HTTPAdapter(max_retries=...))
        # only covers failed DNS lookups, socket connections and connection timeouts
        # It doesnt work when server terminate connection while response is downloaded
    retry = 0
    retry_delay = RETRY_DELAY
    while True:
        try:
            response = session.get(timeout=CONNECT_TIMEOUT, cookies=cookies, *args, **kwargs)
            if response.status_code == 404:
                return
            response.raise_for_status()
            content_length = response.headers.get('Content-Length')
            if content_length is not None and len(response.content) != int(content_length):
                #if content_length is None we repeat anyway to get size and be confident
                raise PartialContentException('Partial response')
            return response
        except (KeyboardInterrupt):
            raise
        except (requests.exceptions.RequestException, PartialContentException) as e:
            if 'url' in kwargs:
                url = kwargs['url']
            elif len(args) > 0:
                url = args[0]
            if retry < MAX_RETRIES:
                print('Retry after exception {0} on {1}'.format(repr(e), url))
                sleep(retry_delay)
                retry_delay = min( 2 * retry_delay, MAX_RETRY_DELAY )
                retry = retry + 1
                continue
            else:
                keep_trying = _retry_prompt(url, repr(e))
                if keep_trying == True:
                    retry = 0
                    continue
                elif keep_trying == False:
                    return
            raise

def get_json(*args, **kwargs):
    """Retrieve text from url. Return text as string or None if no data present """
    resp = safe_get(*args, **kwargs)

    if resp is not None:
        return resp.text