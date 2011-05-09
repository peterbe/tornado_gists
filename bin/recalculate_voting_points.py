#!/usr/bin/env python

import os, sys
if os.path.abspath(os.curdir) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.curdir))
from pymongo import ASCENDING, DESCENDING
from apps.voting.models import Vote, GistPoints, UserPoints
from apps.main.models import User
from apps.gists.models import Gist, Comment
from mongokit import Connection
import settings

def main(*args):
    con = Connection()
    con.register([Vote, GistPoints, UserPoints,
                  User, Gist, Comment])
    db = con[settings.DEFAULT_DATABASE_NAME]

    for user in db.User.find():

        up = db.UserPoints.one({'user.$id': user._id})
        total_up = 0
        if not up:
            up = db.UserPoints()
            up.points = 0
            up.user = user

        for gist in db.Gist.find({'user.$id': user._id}):
            gp = db.GistPoints.one({'gist.$id': gist._id})
            if not gp:
                gp = db.GistPoints()
                gp.gist = gist
                gp.points = 0
            gp.points = sum(x['points'] for x in
                            db.Vote.collection.find({'gist.$id': gist._id}))
            gp.save()
            total_up += gp.points
        up.points = total_up
        up.save()

    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
