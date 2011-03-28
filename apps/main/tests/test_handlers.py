import base64
from pprint import pprint
from time import mktime
import re
import datetime
import simplejson as json

from base import BaseHTTPTestCase
from utils import encrypt_password
import utils.send_mail as mail

class HandlersTestCase(BaseHTTPTestCase):

    def test_homepage(self):
        response = self.get('/')

    def test_user_settings(self):
        return # might not allow this any more
        response = self.get('/user/settings/')
        self.assertEqual(response.code, 200)
        # nothing is checked
        self.assertTrue(not response.body.count('checked'))
        self.assertTrue('name="hide_weekend"' in response.body)
        self.assertTrue('name="monday_first"' in response.body)
        self.assertTrue('name="disable_sound"' in response.body)

        response = self.get('/user/settings.js')
        self.assertEqual(response.code, 200)
        json_str = re.findall('{.*?}', response.body)[0]
        settings = json.loads(json_str)
        self.assertEqual(settings['hide_weekend'], False)
        self.assertEqual(settings['monday_first'], False)

        data = {'hide_weekend':True,
                'disable_sound':True,
                'first_hour':10}
        response = self.post('/user/settings/', data, follow_redirects=False)
        self.assertEqual(response.code, 302)
        guid_cookie = self.decode_cookie_value('guid', response.headers['Set-Cookie'])
        guid = base64.b64decode(guid_cookie.split('|')[0])

        user = self.db.User.one(dict(guid=guid))
        user_settings = self.db.UserSettings.one({
          'user.$id': user._id
        })
        self.assertTrue(user_settings.hide_weekend)
        self.assertTrue(user_settings.disable_sound)
        self.assertEqual(user_settings.first_hour, 10)
        self.assertFalse(user_settings.monday_first)

    def test_signup(self):
        # the get method is just used to validate if an email is used another
        # user
        response = self.get('/user/signup/')
        self.assertEqual(response.code, 404)

        data = {'validate_username': 'peTerbe'}
        response = self.get('/user/signup/', data)
        self.assertEqual(response.code, 200)
        struct = json.loads(response.body)
        self.assertEqual(struct, dict(ok=True))

        user = self.db.users.User()
        user.username = u"PETERBE"
        user.save()

        data = {'validate_username': 'Peterbe'}
        response = self.get('/user/signup/', data)
        self.assertEqual(response.code, 200)
        struct = json.loads(response.body)
        self.assertEqual(struct, dict(error='taken'))

        data = dict(username="peter",
                    email="peterbe@gmail.com",
                    password="secret",
                    first_name="Peter",
                    last_name="Bengtsson")
        response = self.post('/user/signup/', data, follow_redirects=False)
        self.assertEqual(response.code, 302)

        data.pop('password')
        user = self.db.users.User.one(data)
        self.assertTrue(user)

        # a secure cookie would have been set containing the user id
        user_cookie = self.decode_cookie_value('user', response.headers['Set-Cookie'])
        user_id = base64.b64decode(user_cookie.split('|')[0])
        self.assertEqual(str(user._id), user_id)

    def test_change_account(self):

        user = self.db.User()
        user.username = u"peter"
        user.first_name = u"Ptr"
        user.password = encrypt_password(u"secret")
        user.save()

        other_user = self.db.User()
        other_user.username = u'peterbe'
        other_user.save()

        data = dict(username=user.username, password="secret")
        response = self.post('/auth/login/', data, follow_redirects=False)
        self.assertEqual(response.code, 302)
        user_cookie = self.decode_cookie_value('user', response.headers['Set-Cookie'])
        guid = base64.b64decode(user_cookie.split('|')[0])
        self.assertEqual(user.username, u'peter')
        cookie = 'user=%s;' % user_cookie

        response = self.get('/user/', headers={'Cookie':cookie})
        self.assertEqual(response.code, 200)
        self.assertTrue('value="Ptr"' in response.body)

        # not logged in
        response = self.post('/user/', {})
        self.assertEqual(response.code, 403)

        # no username supplied
        response = self.post('/user/', {}, headers={'Cookie':cookie})
        self.assertEqual(response.code, 404)

        data = {'username':'  '}
        response = self.post('/user/', data, headers={'Cookie':cookie})
        self.assertEqual(response.code, 400)

        #data = {'email':'PETERBE@gmail.com'}
        #response = self.post('/user/account/', data, headers={'Cookie':cookie})
        #self.assertEqual(response.code, 400)

        data = {'username':' bob ', 'email':' bob@test.com ', 'last_name': '  Last Name \n'}
        response = self.post('/user/', data, headers={'Cookie':cookie},
                             follow_redirects=False)
        self.assertEqual(response.code, 302)

        user = self.db.User.one(dict(email='bob@test.com'))
        self.assertEqual(user.last_name, data['last_name'].strip())
        user = self.db.User.one(dict(username='bob'))
        self.assertEqual(user.last_name, data['last_name'].strip())
        self.assertEqual(user.first_name, u'')

        # log out
        response = self.get('/auth/logout/', headers={'Cookie':cookie},
                            follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertTrue('user=;' in response.headers['Set-Cookie'])


    def test_help_pages(self):
        return
        # index
        response = self.get('/help/')
        self.assertEqual(response.code, 200)
        self.assertTrue('Help' in response.body)

        # about
        response = self.get('/help/About')
        self.assertEqual(response.code, 200)
        self.assertTrue('Peter Bengtsson' in response.body)

        response = self.get('/help/abOUt')
        self.assertEqual(response.code, 200)
        self.assertTrue('Peter Bengtsson' in response.body)


    def test_reset_password(self):
        # sign up first
        data = dict(username="peterbe",
                    email="peterbe@gmail.com",
                    password="secret",
                    first_name="Peter",
                    last_name="Bengtsson")
        response = self.post('/user/signup/', data, follow_redirects=False)
        self.assertEqual(response.code, 302)

        data.pop('password')
        user = self.db.users.User.one(data)
        self.assertTrue(user)


        response = self.get('/user/forgotten/')
        self.assertEqual(response.code, 200)

        response = self.post('/user/forgotten/', dict(email="bogus"))
        self.assertEqual(response.code, 400)

        response = self.post('/user/forgotten/', dict(email="valid@email.com"))
        self.assertEqual(response.code, 200)
        self.assertTrue('Error' in response.body)
        self.assertTrue('valid@email.com' in response.body)

        response = self.post('/user/forgotten/',
                             dict(email="PETERBE@gmail.com"),
                             follow_redirects=True)
        self.assertEqual(response.code, 200)
        self.assertTrue('instructions sent' in response.body)
        self.assertTrue('peterbe@gmail.com' in response.body)

        sent_email = mail.outbox[-1]
        self.assertTrue('peterbe@gmail.com' in sent_email.to)

        links = [x.strip() for x in sent_email.body.split()
                 if x.strip().startswith('http')]
        from urlparse import urlparse
        link = [x for x in links if x.count('recover')][0]
        # pretending to click the link in the email now
        url = urlparse(link).path
        response = self.get(url)
        self.assertEqual(response.code, 200)

        self.assertTrue('name="password"' in response.body)

        data = dict(password='secret')

        response = self.post(url, data, follow_redirects=False)
        self.assertEqual(response.code, 302)

        user_cookie = self.decode_cookie_value('user', response.headers['Set-Cookie'])
        user_id = base64.b64decode(user_cookie.split('|')[0])
        self.assertEqual(str(user._id), user_id)
        cookie = 'user=%s;' % user_cookie

        response = self.get('/', headers={'Cookie': cookie})
        self.assertTrue("Peter" in response.body)


    def test_change_settings_without_logging_in(self):
        return # no sure whether we're going to allow this
        # without even posting something, change your settings
        db = self.db
        assert not db.UserSettings.find().count()

        data = dict(disable_sound=True, monday_first=True)
        # special client side trick
        data['anchor'] = '#month,2010,11,1'

        response = self.post('/user/settings/', data, follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertTrue(response.headers['Location'].endswith(data['anchor']))

        guid_cookie = self.decode_cookie_value('guid', response.headers['Set-Cookie'])
        cookie = 'guid=%s;' % guid_cookie
        guid = base64.b64decode(guid_cookie.split('|')[0])

        self.assertEqual(db.User.find({'guid':guid}).count(), 1)
        user = db.User.one({'guid':guid})
        self.assertEqual(db.UserSettings.find({'user.$id':user._id}).count(), 1)

        # pick up the cookie and continue to the home page
        response = self.get(response.headers['Location'], headers={'Cookie': cookie})
        self.assertEqual(response.code, 200)
        # the settings we just made will be encoded as a JSON string inside the HTML
        self.assertTrue('"monday_first": true' in response.body)
