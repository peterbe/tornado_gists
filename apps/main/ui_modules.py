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
from utils import gravatar_html, html_quote
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
        return html_quote(truncate_words(string, max_words))

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
    def render(self, gravatar_id, width_and_height=140):
        return gravatar_html(self.handler.is_secure(), gravatar_id, width_and_height)
