#!/usr/bin/env python
import datetime
from urllib import urlopen
import json

def pull_details(username):
    url = "http://github.com/api/v2/json/user/show/%s" % username
    content = urlopen(url).read()
    try:
        return json.loads(content)['user']
    except KeyError:
        return None


def run(max_updates=5):
    from apps.main.models import User
    from mongokit import Connection
    con = Connection()
    con.register([User])
    import settings
    db = con[settings.DEFAULT_DATABASE_NAME]
    print db.User.find().count(), "users in total"
    today = datetime.date.today()
    today = datetime.datetime(*(today.timetuple()[:6]))
    search = {'modify_date': {'$lt': today}}
    print db.User.find(search).count(), "left to update today"
    for user in db.User.find(search).sort('modify_date', 1).limit(max_updates):
        print repr(user.login), user.modify_date
        details = pull_details(user.login)
        if details is None:
            print "FAIL!"
            print "??? http://github.com/api/v2/json/user/show/%s" % user.login
            continue
        for key in 'name company email gravatar_id'.split():
            if key in details:
                if getattr(user, key, '') != details[key]:
                    print "\t", key, repr(getattr(user, key, '*blank*')),
                    print '-->', repr(details[key])
                setattr(user, key, details[key])
        user.modify_date = datetime.datetime.now()
        user.save()

def main(*args):
    max_updates = 100
    if args and args[0].isdigit():
        max_updates = int(args[0])
    run(max_updates=max_updates)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
