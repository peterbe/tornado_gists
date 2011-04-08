from apps.gists.models import Gist
from mongokit import Connection
con = Connection()
con.register([Gist])
import settings

db = con[settings.DEFAULT_DATABASE_NAME]

for key in db.Gist.structure:
    search = {key: {'$exists':False}}
    count = db.Gist.find(search).count()
    if count:
        print "for key", repr(key)
        print "fixing", count, "objects"
        type_ = type(db.Gist.structure[key])
        if type_ is list:
            default_value = []
        elif type_ is unicode:
            default_value = u''
        else:
            raise ValueError("Too hard to guess default value for %r" % type_)

        for each in db.Gist.find(search):
            each[key] = default_value
            each.save()
