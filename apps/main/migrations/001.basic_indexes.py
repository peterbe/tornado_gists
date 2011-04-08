# Note: because this file is run from another python doing execfile() you might
# suffer some weird behaviour if you try to call functions.

from pymongo import ASCENDING, DESCENDING
from apps.main.models import User
from mongokit import Connection
import settings
con = Connection()
con.register([User])
db = con[settings.DEFAULT_DATABASE_NAME]

collection = db.User.collection
collection.ensure_index('login', unique=True, ttl=3000) # default ttl=300

# Test
curs = db.User.find({'login':'peterbe'}).explain()['cursor']
assert 'BtreeCursor' in curs
