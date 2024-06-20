import unittest
from datetime import date
from django.core.exceptions import ValidationError
from courses_apps.guardian.services import child_update
from courses_apps.account.services import user_signup
from courses_apps.guardian.models import Guardian
from courses_apps.learner.models import Learner
from django.contrib.auth import get_user_model

User = get_user_model()

class TestChildUpdate(unittest.TestCase):
    def setUp(self):
        User.objects.filter(email='guardian@example.com').delete()
        self.guardian_user = user_signup(
            username='guardian',
            full_name='Guardian User',
            email='guardian@example.com',
            password='password123',
            confirm_password='password123',
            user_type='guardian',
            bypass_flag=True
        )
        self.guardian = Guardian(user=self.guardian_user)
        self.child_user = user_signup(
            username='child',
            full_name='Child User',
            email='child@example.com',
            password='password123',
            confirm_password='password123',
            user_type='learner',
            bypass_flag=True
        )
        self.child = Learner(user=self.child_user, date_of_birth=date(2005, 1, 1), created_by=self.guardian_user, account_created_by="GUARDIAN")
        self.guardian.children.add(self.child)

    def test_child_update_success(self):
        updated_child = child_update(user=self.guardian_user, child_username='child', full_name='Updated Child', pin='123456')
        self.assertEqual(updated_child.full_name, 'Updated Child')
        self.assertTrue(self.child_user.check_password('123456'))

    def test_child_update_nonexistent_child(self):
        with self.assertRaises(ValidationError):
            child_update(user=self.guardian_user, child_username='nonexistent', full_name='Updated Child')

    def test_child_update_not_guardian_child(self):
        other_child_user = user_signup(
            username='otherchild',
            full_name='Other Child',
            email='otherchild@example.com',
            password='password123',
            confirm_password='password123',
            user_type='learner',
            bypass_flag=True
        )
        other_child = Learner(user=other_child_user, date_of_birth=date(2005, 1, 1), created_by=self.guardian_user, account_created_by="LEARNER")
        with self.assertRaises(ValidationError):
            child_update(user=self.guardian_user, child_username='otherchild', full_name='Updated Child')

    def test_child_update_short_pin(self):
        with self.assertRaises(ValidationError):
            child_update(user=self.guardian_user, child_username='child', pin='123')

    def test_child_update_nonnumeric_pin(self):
        with self.assertRaises(ValidationError):
            child_update(user=self.guardian_user, child_username='child', pin='abcdef')

    def test_child_update_short_username(self):
        with self.assertRaises(ValidationError):
            child_update(user=self.guardian_user, child_username='child', username='abc')

if __name__ == '__main__':
    unittest.main()