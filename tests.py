import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, UserRoles, Role, Sport

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
    

    # User class
    def test_add_roles(self):
        r1 = Role(name='admin')
        r2 = Role(name='user')
        db.session.add_all([r1, r2])
        db.session.commit()
        u = User(username='testuser')
        db.session.add(u)
        db.session.commit()
        u.add_roles('testuser', {'admin': True, 'user': False})
        self.assertEqual(u.get_permissions(), ['admin'])
        u.add_roles('testuser', {'admin': False, 'user': True})
        self.assertEqual(u.get_permissions(), ['user'])

    def test_sign_up_to_sport(self):
        s = Sport(name='football')
        db.session.add(s)
        db.session.commit()
        u = User(username='testuser')
        u.sign_up_to_sport('football')
        self.assertEqual(u.sport_id, s.id)
        u.sign_up_to_sport('baseball')
        self.assertEqual(u.sport_id, s.id)

    def test_unsign_up_to_sport(self):
        s1 = Sport(name='football')
        s2 = Sport(name='baseball')
        db.session.add_all([s1, s2])
        db.session.commit()
        u = User(username='testuser', sport_id=s1.id)
        u.unsign_up_to_sport('football')
        self.assertEqual(u.sport_id, None)
        u = User(username='testuser', sport_id=s2.id)
        u.unsign_up_to_sport('football')
        self.assertEqual(u.sport_id, s2.id)

    # Sport class
    def test_get_user_sign_ups(self):
        s1 = Sport(name='football')
        s2 = Sport(name='baseball')
        db.session.add_all([s1, s2])
        db.session.commit()
        u1 = User(username='testuser', sport_id=s1.id)
        u2 = User(username='testuser2', sport_id=s1.id)
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertEqual(s1.get_user_sign_ups(), 2)
        self.assertEqual(s2.get_user_sign_ups(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)