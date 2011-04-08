from pymongo import ASCENDING, DESCENDING
from models import Gist, Comment
from mongokit import Connection
import settings
con = Connection()
con.register([Gist, Comment])
db = con[settings.DEFAULT_DATABASE_NAME]

def run():
    collection = db.Gist.collection
    collection.ensure_index('gist_id', ttl=3000) # default ttl=300
    collection.ensure_index('user.$id')
    collection.ensure_index('add_date', direction=DESCENDING)

    test()

def test():
    for gist in db.Gist.find():
        curs = db.Gist.find({'gist_id': gist.gist_id}).explain()['cursor']
        assert 'BtreeCursor' in curs
        curs = db.Gist.find({'tags': 'python'}).explain()['cursor']
        assert 'BtreeCursor' in curs
        import re
        curs = db.Gist.find({'tags': re.compile('python', re.I)}).explain()['cursor']
        assert 'BtreeCursor' in curs

        curs = db.Gist.find({'user.$id':gist.user._id}).explain()['cursor']
        assert 'BtreeCursor' in curs
        break
    curs = db.Gist.find().sort('add_date', DESCENDING).limit(1).explain()['cursor']
    assert 'BtreeCursor' in curs
