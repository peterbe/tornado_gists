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

class GistPoints(BaseDocument):
    __collection__ = 'gist_voting_points'
    structure = {
      'gist': Gist,
      'points': int,
    }
    default_values = {
      'points': 0
    }

class UserPoints(BaseDocument):
    __collection__ = 'user_voting_points'
    structure = {
      'user': User,
      'points': int,
    }
    default_values = {
      'points': 0
    }
