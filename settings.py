TITLE = u"GISTS"
APPS = (
  'main',
)

LOGIN_URL = "/auth/login/"
COOKIE_SECRET = "Y2o1TzK2YQAGEYdkL5gmueJIFuY37EQm92XsTo1v/Wi="

WEBMASTER = 'peterbe@gmail.com'
ADMIN_EMAILS = ['peterbe@gmail.com']

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = open('twitter_consumer_secret').read().strip()

DEFAULT_DATABASE_NAME = 'gists'