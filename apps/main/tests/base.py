import re
import unittest
from urllib import urlencode
from cStringIO import StringIO

from tornado.httpclient import HTTPRequest
from tornado.testing import LogTrapTestCase, AsyncHTTPTestCase

import app
from apps.main.models import User
from utils.http_test_client import TestClient, HTTPClientMixin


class BaseModelsTestCase(unittest.TestCase):
    _once = False
    def setUp(self):
        if not self._once:
            self._once = True
            from mongokit import Connection
            self.con = Connection()
            self.con.register([User])
            self.db = self.con.test
            self._emptyCollections()

    def _emptyCollections(self):
        [self.db.drop_collection(x) for x
         in self.db.collection_names()
         if x not in ('system.indexes',)]

    def tearDown(self):
        self._emptyCollections()

class BaseHTTPTestCase(AsyncHTTPTestCase, LogTrapTestCase, HTTPClientMixin):

    _once = False
    def setUp(self):
        super(BaseHTTPTestCase, self).setUp()
        if not self._once:
            self._once = True
            self._emptyCollections()

        self._app.settings['email_backend'] = 'utils.send_mail.backends.locmem.EmailBackend'
        self._app.settings['email_exceptions'] = False
        self.client = TestClient(self)

    def _emptyCollections(self):
        db = self.db
        [db.drop_collection(x) for x
         in db.collection_names()
         if x not in ('system.indexes',)]

    @property
    def db(self):
        return self._app.con[self._app.database_name]

    def get_db(self):
        return self.db
        #return self._app.con[self._app.database_name]

    def get_app(self):
        return app.Application(database_name='test',
                               xsrf_cookies=False,
                               optimize_static_content=False)

    def decode_cookie_value(self, key, cookie_value):
        try:
            return re.findall('%s=([\w=\|]+);' % key, cookie_value)[0]
        except IndexError:
            raise ValueError("couldn't find %r in %r" % (key, cookie_value))

    def reverse_url(self, *args, **kwargs):
        return self._app.reverse_url(*args, **kwargs)
