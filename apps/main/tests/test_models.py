from mongokit import RequireFieldError, ValidationError
import datetime
#import sys; sys.path.insert(0, '..')
from base import BaseModelsTestCase

class ModelsTestCase(BaseModelsTestCase):

    def test_create_user(self):
        user = self.db.User()
        user.username = u'peterbe'
        assert user.add_date
        assert user.modify_date
        user.save()

        inst = self.db.users.User.one()
        assert inst.username
        from utils import encrypt_password
        inst.password = encrypt_password('secret')
        inst.save()

        self.assertFalse(inst.check_password('Secret'))
        self.assertTrue(inst.check_password('secret'))

    def test_user_settings(self):
        user = self.db.User()
        user.username = u'peterbe'
        settings = self.db.UserSettings()

        self.assertRaises(RequireFieldError, settings.save)
        settings.user = user
        settings.save()

        self.assertFalse(settings.newsletter_opt_out)

        model = self.db.UserSettings
        self.assertEqual(model.find({'user.$id': user._id}).count(), 1)

    def test_usersettings_bool_keys(self):
        from apps.main.models import UserSettings
        keys = UserSettings.get_bool_keys()
        self.assertTrue(isinstance(keys, list))
        self.assertTrue(keys) # at least one
        self.assertTrue(isinstance(keys[0], basestring))
