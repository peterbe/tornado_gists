import base64
from pprint import pprint
from time import mktime
import re
import datetime
import json

from base import BaseHTTPTestCase
import utils.send_mail as mail

class HandlersTestCaseBase(BaseHTTPTestCase):

    def setUp(self):
        super(HandlersTestCaseBase, self).setUp()
        # override the otherwise convenient client.login() to one
        # tailored for oauth authentication testing
        from apps.main.handlers import GithubLoginHandler
        GithubLoginHandler.get_authenticated_user = \
          mocked_get_authenticated_user
        self.client.login = self.github_oauth_login

    def github_oauth_login(self, login):
        response = self.client.get('/auth/github/', {'code':'OK-%s'% login})
        self.assertEqual(response.code, 302)


class HandlersTestCase(HandlersTestCaseBase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertTrue(self.reverse_url('github_login') in response.body)

        self.client.login('peterbe')
        response = self.client.get('/')
        self.assertTrue(self.reverse_url('logout') in response.body)
        response = self.client.get(self.reverse_url('logout'))
        self.assertEqual(response.code, 302)
        response = self.client.get('/')
        self.assertTrue(self.reverse_url('github_login') not in response.body)

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


    def test_github_oauth_login(self):
        assert not self.db.User.one({'login':u'peterbe'})
        response = self.client.get('/auth/github/')
        self.assertEqual(response.code, 302)
        self.assertTrue(response.headers['Location'].startswith(
          'https://github.com'))
        response = self.client.get('/auth/github/', {'code':'OK-peterbe'})
        self.assertEqual(response.code, 302)

        self.assertTrue(self.db.User.one({'login':u'peterbe'}))

        response = self.client.get('/')
        self.assertTrue(self.reverse_url('logout') in response.body)
        self.assertTrue(mock_data.MOCK_GITHUB_USERS['peterbe']['name']
                        in response.body)

    def test_github_oauth_failing_login(self):
        response = self.client.get('/auth/github/', {'code':'xxx'})
        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers['Location'],
                         '/?login_failed=true')

    def test_adding_gist(self):
        assert not self.db.Gist.find().count()
        import apps.gists.handlers as _h
        _before = _h.tornado.httpclient.AsyncHTTPClient
        _h.tornado.httpclient.AsyncHTTPClient = MockAsyncHTTPClient
        try:
            response = self.client.post('/add/', {})
            self.assertEqual(response.code, 403)
            self.client.login('peterbe')
            response = self.client.post('/add/', {})
            self.assertEqual(response.code, 400) # no gist id
            response = self.client.post('/add/', {'gist_id':'1234'})
            self.assertEqual(response.code, 302)

            assert self.db.Gist.find().count()
            gist = self.db.Gist.one()
            edit_url = self.reverse_url('edit_gist', gist.gist_id)
            self.assertEqual(edit_url, response.headers['Location'])

            # if you try to add it again it'll redirect to the view url
            response = self.client.post('/add/', {'gist_id':'1234'})
            self.assertEqual(response.code, 302)
            view_url = self.reverse_url('view_gist', gist.gist_id)
            self.assertEqual(view_url, response.headers['Location'])

            # try adding a failing gist that github doesn't recognize
            response = self.client.post('/add/', {'gist_id':'99999'})
            self.assertEqual(response.code, 302)
            self.assertTrue(response.headers['Location'].startswith(
              self.reverse_url('gist_not_found')))

            # poor man's follow redirect
            response = self.client.get(response.headers['Location'])
            assert response.code == 200
            self.assertTrue('Gist not found' in response.body)
            self.assertTrue('https://gist.github.com/99999' in response.body)

        finally:
            _h.tornado.httpclient.AsyncHTTPClient = _before

    def test_viewing_and_edit_gist(self):
        peter = self.db.User()
        peter.login = u'peterbe'
        peter.email = u''
        peter.company = u''
        peter.name = u'Peter'
        peter.save()

        gist = self.db.Gist()
        gist.user = peter
        gist.gist_id = 1234
        gist.created_at = u'yesterday'
        gist.files = [u'foo.py']
        gist.description = u'Testing the Atom feed'
        gist.discussion = u"""Full `markdown` description:
        function foo():
            return bar

[peterbe](http://www.peterbe.com)
        """
        gist.save()

        felinx = self.db.User()
        felinx.login = u'felinx'
        felinx.email = u''
        felinx.company = u'ABC'
        felinx.name = u'Felinx'
        felinx.save()

        gist2 = self.db.Gist()
        gist2.user = felinx
        gist2.gist_id = 555
        gist2.created_at = u'yesterday'
        gist2.files = [u'bar.py']
        gist2.description = u'Another gist'
        gist2.discussion = u"""discuss"""
        gist2.save()

        view_url = self.reverse_url('view_gist', 99999)
        response = self.client.get(view_url)
        self.assertEqual(response.code, 404)

        view_url = self.reverse_url('view_gist', 1234)
        response = self.client.get(view_url)
        self.assertEqual(response.code, 200)
        self.assertTrue('<code>markdown</code>' in response.body)
        self.assertTrue('<code>foo.py</code>' in response.body)
        self.assertTrue(self.reverse_url('by_user', 'peterbe') in response.body)
        self.assertTrue(gist.description in response.body)

        # log in as the owner of it
        self.client.login('peterbe')
        response = self.client.get(view_url)
        self.assertEqual(response.code, 200)
        edit_url = self.reverse_url('edit_gist', 1234)
        delete_url = self.reverse_url('delete_gist', 1234)
        self.assertTrue(edit_url in response.body)
        self.assertTrue(delete_url in response.body)

        other_edit_url = self.reverse_url('edit_gist', 555)
        response = self.client.get(other_edit_url)
        self.assertEqual(response.code, 403)
        other_delete_url = self.reverse_url('delete_gist', 555)
        response = self.client.get(other_delete_url)
        self.assertEqual(response.code, 403)

        response = self.client.get(edit_url)
        self.assertEqual(response.code, 200)
        self.assertTrue('%s</textarea>' % gist.discussion in response.body)

        post_data = {
          'discussion': 'Different',
          'description': 'Short description',
        }
        response = self.client.post(other_edit_url, post_data)
        self.assertEqual(response.code, 403)

        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.code, 302)
        response = self.client.get(view_url)
        self.assertEqual(response.code, 200)
        self.assertTrue('Short description' in response.body)
        self.assertTrue('Different' in response.body)

        response = self.client.get('/')
        self.assertEqual(response.code, 200)
        self.assertTrue(self.reverse_url('by_user', 'peterbe') in response.body)
        self.assertTrue(self.reverse_url('by_user', 'felinx') in response.body)

        response = self.client.get(self.reverse_url('by_user', 'unheardof'))
        self.assertEqual(response.code, 404)

        response = self.client.get(self.reverse_url('by_user', 'peterbe'))
        self.assertEqual(response.code, 200)
        self.assertTrue(self.reverse_url('view_gist', 1234) in response.body)
        self.assertTrue(self.reverse_url('view_gist', 555) not in response.body)
        self.assertTrue(self.reverse_url('by_user', 'felinx') not in response.body)


        self.assertEqual(self.db.Gist.find().count(), 2)
        response = self.client.get(delete_url)
        self.assertEqual(response.code, 302)
        self.assertEqual(self.db.Gist.find().count(), 1)

import mock_data
def mocked_get_authenticated_user(self, code, callback, **kwargs):
    if code.startswith('OK') and len(code.split('OK-')) == 2:
        callback(mock_data.MOCK_GITHUB_USERS[code.split('OK-')[1]])
    else:
        callback({})

class _FakeBody(dict):
    def __getattr__(self, key):
        return self[key]


class MockAsyncHTTPClient(object):
    def fetch(self, url, callback):
        gist_id = url.split('/')[-1]
        gist = mock_data.MOCK_GISTS.get(str(gist_id), {})
        callback(_FakeBody({'body':json.dumps(gist)}))
