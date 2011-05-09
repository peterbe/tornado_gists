import os

_ROOT = os.path.dirname(__file__)

TITLE = u"Tornado Gists"
SUB_TITLE = "explaining Tornado on gist at a time"
DOMAIN_NAME = "TornadoGists.org"
APPS = (
  'main',
  'gists',
  'voting',
)

LOGIN_URL = "/auth/login/"
COOKIE_SECRET = "Y2o1TzK2YQAGEYdkL5gmueJIFuY37EQm92XsTo1v/Wi="

WEBMASTER = 'felinx.lee@gmail.com'
ADMIN_EMAILS = ['felinx.lee@gmail.com', 'peterbe@gmail.com']

DEFAULT_DATABASE_NAME = 'tornadogists'

OAUTH_SETTINGS = {
    'client_id': '505fee7706f024a2bcc1',
    'client_secret': open(os.path.join(_ROOT, 'github_client_secret')).read().strip(),
    'base_url': 'https://github.com/login/oauth/',
    'redirect_url': 'http://tornadogists.org/auth/github/' # can this be localhost:8000/...?
}

try:
    from local_settings import *
except ImportError:
    pass
