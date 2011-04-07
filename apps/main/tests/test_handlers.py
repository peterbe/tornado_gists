import base64
from pprint import pprint
from time import mktime
import re
import datetime

from base import BaseHTTPTestCase
import utils.send_mail as mail

class HandlersTestCase(BaseHTTPTestCase):

    def test_homepage(self):
        response = self.client.get('/')

    def test_latest_feeds_atom(self):
        response = self.client.get('/feeds/atom/latest/')
        self.assertEqual(response.code, 200)
        self.assertTrue('<feed' in response.body)

        # add a fake user
        peter = self.db.User()
        peter.login = u'peterbe'
        peter.email = u''
        peter.company = u''
        peter.name = u'Peter'
        peter.save()

        gist1 = self.db.Gist()
        gist1.user = peter
        gist1.gist_id = 1234
        gist1.description = u'Testing the Atom feed'
        gist1.discussion = u"""Full `markdown` description:
        function foo():
            return bar

        (peterbe)[http://www.peterbe.com]
        """
        gist1.save()

        response = self.client.get('/feeds/atom/latest/')
        assert response.code == 200
        # because the feed was only added about 0 seconds ago
        # it won't be included
        self.assertTrue('<entry' not in response.body)
        gist1.add_date -= datetime.timedelta(minutes=1)
        gist1.save()

        response = self.client.get('/feeds/atom/latest/')
        assert response.code == 200
        self.assertTrue('<entry' in response.body)
        self.assertTrue(self.reverse_url('view_gist', gist1.gist_id) in response.body)
        self.assertTrue('<name>Peter</name>' in response.body)

        gist2 = self.db.Gist()
        gist2.user = peter
        gist2.gist_id = 8888
        gist2.description = u'Artifically created long ago'
        gist2.save()
        gist2.add_date -= datetime.timedelta(hours=1)
        gist2.save()

        response = self.client.get('/feeds/atom/latest/')
        assert response.code == 200
        self.assertTrue(-1 < response.body.find('<id>1234</id>') <\
                             response.body.find('<id>8888</id>'))
