import unittest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses_apps.guardian.services import guardian_signup

User = get_user_model()

class TestGuardianSignup(TestCase):
    def test_guardian_signup_success(self):
        email = 'test@example.com'
        username= 'test_guardian'
        password = 'strongpassword1$'
        confirm_password = 'strongpassword1$'

        signup_details, refresh_token = guardian_signup(
            email=email,
            password=password,
            confirm_password=confirm_password
        )

        self.assertEqual(signup_details.user_type, 'guardian')
        self.assertTrue(signup_details.username)
        self.assertEqual(signup_details.email, email.lower())
        self.assertFalse(signup_details.is_verified)
        self.assertTrue(signup_details.access_token)

    def test_guardian_signup_existing_email(self):
        email = 'test@example.com'
        password = 'strongpassword1$'
        confirm_password = 'strongpassword1$'

        # Mocking user_signup function to simulate existing email
        def mocked_user_signup(**kwargs):
            raise ValidationError("User with the email already exists.")

        with unittest.mock.patch('courses_apps.guardian.services.user_signup', new=mocked_user_signup):
            with self.assertRaises(ValidationError) as context:
                guardian_signup(
                    email=email,
                    password=password,
                    confirm_password=confirm_password
                )
        self.assertEqual(str(context.exception.message), "User with the email already exists.")


if __name__ == '__main__':
    unittest.main()