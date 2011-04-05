import re
import random

def niceboolean(value):
    if type(value) is bool:
        return value
    falseness = ('','no','off','false','none','0', 'f')
    return str(value).lower().strip() not in falseness


email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
def valid_email(email):
    return bool(email_re.search(email))



from random import choice
from string import letters
def random_string(length):
    return ''.join(choice(letters) for i in xrange(length))

def gravatar_html(is_secure, gravatar_id, width_and_height=140):
    # this is how github does it
    if is_secure:
        src = 'https://secure.gravatar.com/avatar/%s' % gravatar_id
    else:
        src = 'http://gravatar.com/avatar/%s' % gravatar_id
    width = height = int(width_and_height)
    src += '?s=%s' % width
    src += '&d=https://d3nwyuy0nl342s.cloudfront.net%2Fimages%2Fgravat'\
           'ars%2Fgravatar-140.png'
    tmpl = '<img width="%s" height="%s" alt="" class="gravatar" src="%s"/>'
    return tmpl % (width, height, src)

def html_quote(text):
    return text.replace('<','&lt').replace('>','&gt').replace('"','&quot;')