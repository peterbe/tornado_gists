import datetime
from pymongo.objectid import ObjectId
from apps.main.models import BaseDocument, User
from apps.gists.models import Gist, Comment

class Vote(BaseDocument):
    __collection__ = 'votes'
    structure = {
      'user': User,
      'gist': Gist,
      'comment': Comment,
      'points': int
    }

    default_values = {
      'points': 1,
    }
