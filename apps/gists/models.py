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
      'tags': [unicode],
      'discussion': unicode,
      'discussion_format': unicode,
      # persistent cache attributes
      'contents': [unicode],
    }

    default_values = {
      'discussion': u'',
      'discussion_format': u'markdown',
    }

    @property
    def no_comments(self):
        _no_comments = getattr(self, '_no_comments', None)
        if _no_comments is None:
            _no_comments = self.db.Comment.find({'gist.$id':self._id}).count()
            self._no_comments = _no_comments
        return _no_comments


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

    @property
    def file_index_number(self):
        if self.file:
            return self.gist.files.index(self.file)
        return 0
