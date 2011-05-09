from pymongo import ASCENDING, DESCENDING
from models import User
from mongokit import Connection
import settings
con = Connection()
con.register([User])
db = con[settings.DEFAULT_DATABASE_NAME]

def run():
    collection = db.User.collection
    collection.ensure_index('login', unique=True, ttl=3000) # default ttl=300
    yield 'login'
    test()

def test():
    curs = db.User.find({'login':'abc123'}).explain()['cursor']
    assert 'BtreeCursor' in curs
