from mongokit import RequireFieldError, ValidationError
import datetime
#import sys; sys.path.insert(0, '..')
from apps.main.tests.base import BaseModelsTestCase
from apps.gists.models import Gist, Comment
#from apps.main.models import User

class ModelsTestCase(BaseModelsTestCase):

    def setUp(self):
        super(ModelsTestCase, self).setUp()
        self.con.register([Gist, Comment])


    def test_gist(self):
        user = self.db.User()
        user.login = u'peterbe'
        user.save()

        gist = self.db.Gist()
        gist.user = user
        gist.gist_id = 1
        gist.description = u'Description'
        gist.files = [u'foo.py', u'bar.js']
        gist.save()

        assert gist.no_comments == 0

    def test_comment(self):
        user = self.db.User()
        user.login = u'peterbe'
        user.save()

        gist = self.db.Gist()
        gist.user = user
        gist.gist_id = 1
        gist.description = u'Description'
        gist.files = [u'foo.py', u'bar.js']
        gist.save()

        comment = self.db.Comment()
        comment.gist = gist
        comment.user = user
        comment.comment = u"Works"
        comment.comment_format = u"markdown"
        comment.file = u'bar.js'
        comment.save()

        self.assertEqual(comment.file_index_number, 1)
