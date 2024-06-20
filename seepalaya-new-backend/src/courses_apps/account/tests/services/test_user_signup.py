import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from courses_apps.account.services import user_signup
from courses_apps.account.models import PortalUser
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
User = get_user_model()

class TestUserSignup(TestCase):
    @patch('courses_apps.account.selectors.check_if_email_is_taken', return_value=None)
    @patch('courses_apps.account.selectors.user_get_from_username', return_value=None)
    @patch('courses_apps.account.selectors.get_user_role_by_name')
    def test_user_signup_success(self, mocked_get_user_role_by_name, mocked_user_get_from_username, mocked_check_if_email_is_taken):
        mocked_get_user_role_by_name.return_value = MagicMock()
        username='testuser'
        full_name = 'Test User'
        email = 'test@example.com'
        password = 'strongpassword1$'
        confirm_password = 'strongpassword1$'
        user_type = 'learner'

        user = user_signup(
            username=username,
            full_name=full_name,
            email=email,
            password=password,
            confirm_password=confirm_password,
            user_type=user_type
        )

        self.assertEqual(user.full_name, full_name)
        self.assertEqual(user.email, email.lower())
        self.assertFalse(user.is_verified)

    @patch('courses_apps.account.selectors.check_if_email_is_taken', return_value=get_user_model()())
    def test_user_signup_existing_email(self, mocked_check_if_email_is_taken):
        username='testuser'
        full_name = 'Test User'
        email = 'test@example.com'
        password = 'strongpassword1$'
        confirm_password = 'strongpassword1$'
        user_type = 'learner'

        user = user_signup(
            username=username,
            full_name=full_name,
            email=email,
            password=password,
            confirm_password=confirm_password,
            user_type=user_type
        )

        self.assertEqual(user.email, email)

    def test_empty_password_fields(self):
        with self.assertRaises(ValidationError):
            user_signup(
                username='testuser',
                full_name = 'Test User',
                email='test@example.com',
                password='',
                confirm_password='',
                user_type='learner'
            )

    def test_password_mismatch(self):
        with self.assertRaises(ValidationError):
            user_signup(
                username='testuser',
                full_name = 'Test User',
                email='test@example.com',
                password='strongpassword1$',
                confirm_password='differentpassword1$',
                user_type='learner'
            )
        
if __name__ == '__main__':
    unittest.main()
