from pymongo import ASCENDING, DESCENDING
from models import Gist, Comment
from mongokit import Connection
import settings
con = Connection()
con.register([Gist, Comment])
db = con[settings.DEFAULT_DATABASE_NAME]

def run():
    collection = db.Gist.collection
    collection.ensure_index([('add_date',DESCENDING)])
    yield 'add_date'
    collection.ensure_index('gist_id')
    yield 'gist_id'
    collection.ensure_index('tags')
    yield 'tags'
    collection.ensure_index('user.$id') # default ttl=300
    yield 'user.$id'

    collection = db.Comment.collection
    collection.ensure_index('user.$id')
    yield 'user.$id'
    collection.ensure_index('gist.$id')
    yield 'gist.$id'
    collection.ensure_index([('add_date',DESCENDING)])
    yield 'add_date'

    test()


def test():
    curs = db.Gist.find().sort('add_date', DESCENDING).explain()['cursor']
    assert 'BtreeCursor' in curs

    curs = db.Gist.find({'gist_id':'abc123'}).explain()['cursor']
    assert 'BtreeCursor' in curs

    any_obj_id = list(db.Gist.find().limit(1))[0]._id
    curs = db.Gist.find({'user.$id':any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs

    curs = db.Gist.find({'tags': {'$in':['abc123']}}).explain()['cursor']
    assert 'BtreeCursor' in curs

    db.Comment.find({'user.$id': any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs

    db.Comment.find({'gist.$id': any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs
