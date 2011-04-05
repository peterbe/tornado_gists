# python
import traceback
import urllib
import cgi
from random import random
import httplib
from hashlib import md5
from cStringIO import StringIO
from urlparse import urlparse
from pprint import pprint
from collections import defaultdict
from time import mktime, sleep
import datetime
from urllib import quote
import os.path
import re
import logging

from pymongo.objectid import InvalidId, ObjectId
from pymongo import ASCENDING, DESCENDING

# tornado
import tornado.auth
import tornado.web
import tornado.escape
from tornado import httpclient

# app
from utils.routes import route, route_redirect
from utils.send_mail import send_email
from utils.decorators import login_required
import settings

class HTTPSMixin(object):

    def is_secure(self):
        # XXX is this really the best/only way?
        return self.request.headers.get('X-Scheme') == 'https'

    def httpify_url(self):
        return self.request.full_url().replace('https://', 'http://')

    def httpsify_url(self):
        return self.request.full_url().replace('http://', 'https://')


class BaseHandler(tornado.web.RequestHandler, HTTPSMixin):

    @property
    def db(self):
        return self.application.con[self.application.database_name]

    def xxx_handle_request_exception(self, exception):
        if not isinstance(exception, tornado.web.HTTPError) and \
          not self.application.settings['debug']:
            # ie. a 500 error
            try:
                self._email_exception(exception)
            except:
                print "** Failing even to email exception **"

        if self.application.settings['debug']:
            # Because of
            # https://groups.google.com/d/msg/python-tornado/Zjv6_3OYaLs/CxkC7eLznv8J
            print "Exception!"
            print exception
        super(BaseHandler, self)._handle_request_exception(exception)

    def xxx_log(self):
        """overwritten from tornado.web.RequestHandler because we want to put
        all requests as logging.debug and keep all normal logging.info()"""
        if self._status_code < 400:
            #log_method = logging.info
            log_method = logging.debug
        elif self._status_code < 500:
            log_method = logging.warning
        else:
            log_method = logging.error
        request_time = 1000.0 * self.request.request_time()
        log_method("%d %s %.2fms", self._status_code,
                   self._request_summary(), request_time)


    def _email_exception(self, exception): # pragma: no cover
        import sys
        err_type, err_val, err_traceback = sys.exc_info()
        error = u'%s: %s' % (err_type, err_val)
        out = StringIO()
        subject = "%r on %s" % (err_val, self.request.path)
        print >>out, "TRACEBACK:"
        traceback.print_exception(err_type, err_val, err_traceback, 500, out)
        traceback_formatted = out.getvalue()
        print traceback_formatted
        print >>out, "\nREQUEST ARGUMENTS:"
        arguments = self.request.arguments
        if arguments.get('password') and arguments['password'][0]:
            password = arguments['password'][0]
            arguments['password'] = password[:2] + '*' * (len(password) -2)
        pprint(arguments, out)

        print >>out, "\nCOOKIES:"
        for cookie in self.cookies:
            print >>out, "  %s:" % cookie,
            print >>out, repr(self.get_secure_cookie(cookie))

        print >>out, "\nREQUEST:"
        for key in ('full_url', 'protocol', 'query', 'remote_ip',
                    'request_time', 'uri', 'version'):
            print >>out, "  %s:" % key,
            value = getattr(self.request, key)
            if callable(value):
                try:
                    value = value()
                except:
                    pass
            print >>out, repr(value)

        print >>out, "\nGIT REVISION: ",
        print >>out, self.application.settings['git_revision']

        print >>out, "\nHEADERS:"
        pprint(dict(self.request.headers), out)

        send_email(self.application.settings['email_backend'],
                   subject,
                   out.getvalue(),
                   self.application.settings['webmaster'],
                   self.application.settings['admin_emails'],
                   )

    def get_current_user(self):
        # the 'user' cookie is for securely logged in people
        user_id = self.get_secure_cookie("user")
        if user_id:
            return self.db.User.one({'_id': ObjectId(user_id)})

    # shortcut where the user parameter is not optional
    def get_user_settings(self, user, fast=False):
        return self.get_current_user_settings(user=user, fast=fast)

    def get_current_user_settings(self, user=None, fast=False):
        if user is None:
            user = self.get_current_user()

        if not user:
            raise ValueError("Can't get settings when there is no user")
        _search = {'user.$id': user['_id']}
        if fast:
            return self.db[UserSettings.__collection__].one(_search) # skip mongokit
        else:
            return self.db.UserSettings.one(_search)

    def create_user_settings(self, user, **default_settings):
        user_settings = self.db.UserSettings()
        user_settings.user = user
        for key in default_settings:
            setattr(user_settings, key, default_settings[key])
        user_settings.save()
        return user_settings

    def get_cdn_prefix(self):
        """return something that can be put in front of the static filename
        E.g. if filename is '/static/image.png' and you return '//cloudfront.com'
        then final URL presented in the template becomes
        '//cloudfront.com/static/image.png'
        """
        return self.application.settings.get('cdn_prefix')

    def write_json(self, struct, javascript=False):
        if javascript:
            self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(tornado.escape.json_encode(struct))


    def serialize_dict(self, data):
        for key, value in data.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                data[key] = mktime(value.timetuple())
        return data

    def find_user(self, username):
        return self.db.User.one(dict(username=\
         re.compile('^%s$' % re.escape(username), re.I)))

    def find_user_by_email(self, email):
        return self.db.User.one(dict(email=\
         re.compile('^%s$' % re.escape(email), re.I)))

    def has_user(self, username):
        return bool(self.find_user(username))

    def is_admin_user(self, user):
        return user.email in settings.ADMIN_EMAILS

    def get_base_options(self):
        # The templates rely on these variables
        options = dict(user=None,
                       user_name=None,
                       is_admin_user=False)

        # default settings
        settings = dict(
                        disable_sound=False,
                        )

        user = self.get_current_user()
        user_name = None

        if user:
            if self.get_secure_cookie('user'):
                options['user'] = user
                options['is_admin_user'] = self.is_admin_user(user)
                if user.name:
                    user_name = user.name
                elif user.email:
                    user_name = user.email
                else:
                    user_name = "stranger"
                options['user_name'] = user_name

            # override possible settings
            user_settings = self.get_current_user_settings(user)

        options['settings'] = settings
        options['git_revision'] = self.application.settings['git_revision']
        options['debug'] = self.application.settings['debug']
        return options


@route('/', name="home")
class HomeHandler(BaseHandler):

    def get(self, by=None):
        options = self.get_base_options()
        user = options['user']
        gists_search = {}
        comment_search = {}
        if by is not None:
            gists_search = {'user.$id': by._id}
            comment_search = {'user.$id': by._id}
        options['by'] = by
        options['gists'] = self.db.Gist.find(gists_search)\
          .sort('add_date', DESCENDING)

        options['recent_comments'] = self.db.Comment.find(comment_search)\
          .sort('add_date', DESCENDING).limit(20)

        self.render("home.html", **options)

@route('/by/(\w+)', name="by_user")
class ByLoginHomeHandler(HomeHandler):

    def get(self, login):
        user = self.db.User.one({'login':login})
        if not user:
            raise tornado.web.HTTPError(404, "No user by that login")
        super(ByLoginHomeHandler, self).get(by=user)

class BaseAuthHandler(BaseHandler):

    def get_next_url(self, default='/'):
        next = default
        if self.get_argument('next', None):
            next = self.get_argument('next')
        elif self.get_cookie('next', None):
            next = self.get_cookie('next')
            self.clear_cookie('next')
        return next

class CredentialsError(Exception):
    pass


class GithubMixin(tornado.auth.OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token?"
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize?"
    _OAUTH_NO_CALLBACKS = False

    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, extra_fields=None):
        """handles login"""
        http = httpclient.AsyncHTTPClient()
        args = {
          "redirect_uri": redirect_uri,
          "code": code,
          "client_id": client_id,
          "client_secret": client_secret,
        }
        print "ARGS"
        print args

        fields = set(['id', 'name', 'first_name', 'last_name',
                      'locale', 'picture', 'link'])
        if extra_fields:
            fields.update(extra_fields)

        url = self._oauth_request_token_url(**args)
        print "** URL", repr(url)
        http.fetch(url,
          self.async_callback(self._on_access_token, redirect_uri, client_id,
                              client_secret, callback, fields))

    def _on_access_token(self, redirect_uri, client_id, client_secret,
                        callback, fields, response):
        if response.error:
            logging.warning('Facebook auth error: %s' % str(response))
            callback(None)
            return

        #print "self.request.arguments"
        #print self.request.arguments
        #print "RESPONSE.BODY:"
        #print response.body

        session = {
          "access_token": cgi.parse_qs(response.body)["access_token"][-1],
          "expires": cgi.parse_qs(response.body).get("expires")
        }
        #print "SESSION"
        #print session
        #print "\n"

        self.github_request(
          path="/user/show",
          callback=self.async_callback(
              self._on_get_user_info, callback, session, fields),
          access_token=session["access_token"],
          fields=",".join(fields)
          )


    def _on_get_user_info(self, callback, session, fields, user):
        if user is None:
            callback(None)
            return

        #pprint(user)
        fieldmap = user['user']
        print 'session.get("expires")', repr(session.get("expires"))

        fieldmap.update({"access_token": session["access_token"],
                         "session_expires": session.get("expires")})
        callback(fieldmap)


    def github_request(self, path, callback, access_token=None,
                           post_args=None, **args):
        """
        """
        url = "https://github.com/api/v2/json" + path
        all_args = {}
        if access_token:
            all_args["access_token"] = access_token
            all_args.update(args)
            all_args.update(post_args or {})
        if all_args: url += "?" + urllib.urlencode(all_args)
        callback = self.async_callback(self._on_github_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_github_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                            response.request.url)
            callback(None)
            return
        callback(tornado.escape.json_decode(response.body))


@route('/auth/github/')
class GithubLoginHandler(BaseAuthHandler, GithubMixin):

    @tornado.web.asynchronous
    def get(self):
        settings_ = settings.OAUTH_SETTINGS
        if self.get_argument("code", False):
            self.get_authenticated_user(
                  redirect_uri=settings_['redirect_url'],
                  client_id=settings_['client_id'],
                  client_secret=settings_['client_secret'],
                  code=self.get_argument("code"),
                  callback=self.async_callback(
                    self._on_login))
            return

        self.authorize_redirect(redirect_uri=settings_['redirect_url'],
                                client_id=settings_['client_id'],
                                extra_params={})#"scope": "read_stream,offline_access"})

    def _on_login(self, github_user):
        user = self.db.User.one({'login':github_user['login']})
        if user is None:
            user = self.db.User()
            user.login = github_user['login']
            print "CREATE NEW USER"
        for key in ('email','name','company','gravatar_id','access_token'):
            if key in github_user:
                setattr(user, key, unicode(github_user[key]))
        user.save()
        print repr(user)
        self.set_secure_cookie("user", str(user._id), expires_days=100)

        self.redirect('/')
        #logging.error(user)



@route(r'/auth/logout/')
class AuthLogoutHandler(BaseAuthHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect(self.get_next_url())
