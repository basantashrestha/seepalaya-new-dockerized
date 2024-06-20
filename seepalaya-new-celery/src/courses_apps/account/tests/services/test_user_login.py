import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from courses_apps.account.services import user_login
from rest_framework.exceptions import ValidationError

User = get_user_model()

class TestUserLogin(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='strongpassword1$'
        )
        self.user.is_verified = True  # Set is_verified to True
        self.user.save()

    def test_user_login_success(self):
        username_or_email = 'testuser'
        password = 'strongpassword1$'

        login_details, refresh_token = user_login(
            username_or_email=username_or_email,
            password=password
        )

        self.assertEqual(login_details.username, self.user.username)
        self.assertEqual(login_details.user_email, self.user.email)
        self.assertEqual(login_details.full_name, self.user.full_name)
        self.assertTrue(login_details.is_verified)
        self.assertTrue(login_details.access_token)

    def test_user_login_invalid_password(self):
        username_or_email = 'testuser'
        password = 'wrongpassword'

        with self.assertRaises(ValidationError) as context:
            user_login(
                username_or_email=username_or_email,
                password=password
            )

        self.assertEqual(str(context.exception.detail[0]), "Invalid credentials.")

    def test_user_login_invalid_credentials(self):
        username_or_email = 'unknownuser'
        password = 'strongpassword1$'

        with self.assertRaises(ValidationError) as context:
            user_login(
                username_or_email=username_or_email,
                password=password
            )

        self.assertEqual(str(context.exception.detail[0]), "Invalid credentials.")


if __name__ == '__main__':
    unittest.main()