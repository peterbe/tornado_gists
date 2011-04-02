import os

_ROOT = os.path.dirname(__file__)

TITLE = u"Tornado Gists"
APPS = (
  'main',
  'gists',
)

LOGIN_URL = "/auth/login/"
COOKIE_SECRET = "Y2o1TzK2YQAGEYdkL5gmueJIFuY37EQm92XsTo1v/Wi="

WEBMASTER = 'felinx.lee@gmail.com'
ADMIN_EMAILS = ['felinx.lee@gmail.com']

#TWITTER_CONSUMER_KEY = ''
#TWITTER_CONSUMER_SECRET = open(os.path.join(_ROOT, 'twitter_consumer_secret')).read().strip()

DEFAULT_DATABASE_NAME = 'tornadogists'

oauth_settings = {
    'client_id': '505fee7706f024a2bcc1',
    'client_secret': open(os.path.join(_ROOT, 'github_client_secret')).read().strip(),
    'base_url': 'https://github.com/login/oauth/',
    'redirect_url': 'http://tornadogists.org/auth/github/' # can this be localhost:8000/...?
    #'redirect_url': 'http://localhost:8000/auth/github/',
}
