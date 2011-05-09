from pymongo import ASCENDING, DESCENDING
from models import Vote, GistPoints, UserPoints
from mongokit import Connection
import settings
con = Connection()
con.register([Vote, GistPoints, UserPoints])
db = con[settings.DEFAULT_DATABASE_NAME]

def run():
    collection = db.Vote.collection
    collection.ensure_index('user.$id')
    yield 'user.$id'
    collection.ensure_index('gist.$id')
    yield 'user.$id'

    collection = db.GistPoints.collection
    collection.ensure_index('gist.$id')
    yield 'user.$id'
    collection.ensure_index([('points',DESCENDING)])
    yield 'points'

    collection = db.UserPoints.collection
    collection.ensure_index('user.$id')
    yield 'user.$id'
    collection.ensure_index([('points',DESCENDING)])
    yield 'points'

    test()


def test():
    any_obj_id = list(db.Vote.find().limit(1))[0]._id
    curs = db.Vote.find({'user.$id':any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs
    curs = db.Vote.find({'gist.$id':any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs

    curs = db.GistPoints.find({'gist.$id':any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs
    curs = db.GistPoints.find().sort('points', DESCENDING).explain()['cursor']
    assert 'BtreeCursor' in curs
    curs = db.UserPoints.find({'user.$id':any_obj_id}).explain()['cursor']
    assert 'BtreeCursor' in curs
    curs = db.UserPoints.find().sort('points', DESCENDING).explain()['cursor']
    assert 'BtreeCursor' in curs
