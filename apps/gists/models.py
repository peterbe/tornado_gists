from pymongo.objectid import ObjectId
import datetime
from apps.main.models import BaseDocument, User

class Gist(BaseDocument):
    __collection__ = 'gists'
    structure = {
      'user': User,
      'gist_id': int,
      # basic Gist information
      'description': unicode,
      'files':[unicode],
      'created_at': unicode, #datetime.datetime,
      'public': bool,
      'owner': unicode,
      'repo': unicode,
      # extra
      'discussion': unicode,
      'discussion_format': unicode,
      # persistent cache attributes
      'contents': [unicode],
    }

    default_values = {
      'discussion': u'',
      'discussion_format': u'markdown',
    }


class Comment(BaseDocument):
    __collection__ = 'comments'
    structure = {
      'user': User,
      'gist': Gist,
      'comment': unicode,
      'comment_format': unicode,
      'file': unicode,
      'line': int,
      'reply_to': ObjectId
    }