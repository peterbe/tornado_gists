from mongokit import RequireFieldError, ValidationError
import datetime
#import sys; sys.path.insert(0, '..')
from base import BaseModelsTestCase

class ModelsTestCase(BaseModelsTestCase):

    def test_create_user(self):
        user = self.db.User()
        user.login = u'peterbe'
        assert user.add_date
        assert user.modify_date
        user.save()

        inst = self.db.users.User.one()
        assert inst.login
        inst.save()
