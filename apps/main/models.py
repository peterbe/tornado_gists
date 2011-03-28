import datetime
from mongokit import Document, ValidationError

class BaseDocument(Document):
    structure = {
      'add_date': datetime.datetime,
      'modify_date': datetime.datetime,
    }

    default_values = {
      'add_date': datetime.datetime.now,
      'modify_date': datetime.datetime.now
    }
    use_autorefs = True
    use_dot_notation = True


class User(BaseDocument):
    # modelled on the Github user account
    __collection__ = 'users'
    structure = {
      'login': unicode,
      'email': unicode,
      'company': unicode,
      'name': unicode,
      'gravatar_id': unicode,
      'access_token': unicode,
    }

    use_autorefs = True
    required_fields = ['login']

    #indexes = [
    #  {'fields': 'guid',
    #   'unique': True},
    #]
