import markdown
import datetime
import re
from base64 import encodestring
import stat
import os
import cPickle
from time import time
import marshal
from tempfile import gettempdir
import tornado.web
import tornado.escape
from utils.timesince import smartertimesince
from subprocess import Popen, PIPE
from utils.truncate import truncate_words

class Footer(tornado.web.UIModule):
    def render(self, user=None):
        return self.render_string("modules/footer.html",
          calendar_link=self.request.path != '/',
          user=user,
         )

class TruncateWords(tornado.web.UIModule):
    def render(self, string, max_words=20):
        return truncate_words(string, max_words)

class TruncateString(tornado.web.UIModule):
    def render(self, string, max_length=30):
        if len(string) > max_length:
            return string[:max_length] + '...'
        return string


class TimeSince(tornado.web.UIModule):
    def render(self, date, date2=None):
        return smartertimesince(date, date2)

class RenderText(tornado.web.UIModule):
    def render(self, text, format='plaintext'):
        if format == 'markdown':
            return markdown.markdown(text, safe_mode="escape")
        else:
            # plaintext
            html = '<p>%s</p>' % tornado.escape.linkify(text).replace('\n','<br>\n')
        return html

class ShowGravatar(tornado.web.UIModule):
    def render(self, gravatar_id, width_and_height=140, secure=False):
        print "secure",
        # this is how github does it
        if self.handler.is_secure():
            src = 'https://secure.gravatar.com/avatar/%s' % gravatar_id
        else:
            src = 'http://gravatar.com/avatar/%s' % gravatar_id
        width = height = int(width_and_height)
        src += '?s=%s' % width
        src += '&d=https://d3nwyuy0nl342s.cloudfront.net%2Fimages%2Fgravat'\
               'ars%2Fgravatar-140.png'
        tmpl = '<img width="%s" height="%s" alt="" class="gravatar" src="%s"/>'
        return tmpl % (width, height, src)
