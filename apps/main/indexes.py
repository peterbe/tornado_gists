from pymongo import ASCENDING, DESCENDING
from models import User
from mongokit import Connection
con = Connection()
con.register([User])
db = con.worklog

def run():
    collection = db.User.collection
    collection.ensure_index('login', unique=True, ttl=3000) # default ttl=300
    test()

def test():
    curs = db.User.find({'login':'peterbe'}).explain()['cursor']
    assert 'BtreeCursor' in curs
