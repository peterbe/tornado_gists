TITLE = u"GISTS"
APPS = (
  'main',
  'gists',
)

LOGIN_URL = "/auth/login/"
COOKIE_SECRET = "Y2o1TzK2YQAGEYdkL5gmueJIFuY37EQm92XsTo1v/Wi="

WEBMASTER = 'peterbe@gmail.com'
ADMIN_EMAILS = ['peterbe@gmail.com']

#TWITTER_CONSUMER_KEY = ''
#TWITTER_CONSUMER_SECRET = open('twitter_consumer_secret').read().strip()

DEFAULT_DATABASE_NAME = 'gists'

oauth_settings = {
    'client_id': '1ccb7f00082bc45047e7',
    'client_secret': open('github_client_secret').read().strip(),
    'base_url': 'https://github.com/login/oauth/',
    'redirect_url': 'http://www.peterbe.com/tornadogists/callback' # can this be localhost:8000/...?
    #'redirect_url': 'http://localhost:8000/auth/github/',
}