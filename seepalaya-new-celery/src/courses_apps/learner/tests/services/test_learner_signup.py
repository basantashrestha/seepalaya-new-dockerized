import unittest
from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses_apps.learner.services import learner_signup

User = get_user_model()

class TestLearnerSignup(TestCase):
    def test_learner_signup_success(self):
        full_name = "Learner Name"
        email = 'test@example.com'
        password = 'strongpassword1$'
        confirm_password = 'strongpassword1$'

        signup_details, refresh_token = learner_signup(
            full_name=full_name,
            email=email,
            password=password,
            confirm_password=confirm_password
        )
        self.assertEqual(signup_details.full_name, full_name)
        self.assertTrue(signup_details.username)
        self.assertEqual(signup_details.user_email, email.lower())
        self.assertFalse(signup_details.is_verified)
        self.assertTrue(signup_details.access_token)

    def test_learner_signup_existing_email(self):
        full_name = "Learner Name"
        email = 'test@example.com'
        password = 'strongpassword1$'
        confirm_password = 'strongpassword1$'

        # Mocking user_signup function to simulate existing email
        def mocked_user_signup(**kwargs):
            raise ValidationError("User with the email already exists.")

        with unittest.mock.patch('courses_apps.learner.services.user_signup', side_effect=mocked_user_signup):
            with self.assertRaises(ValidationError) as context:
                learner_signup(
                    full_name=full_name,
                    email=email,
                    password=password,
                    confirm_password=confirm_password
                )

        self.assertEqual(str(context.exception.message), "User with the email already exists.")


if __name__ == '__main__':
    unittest.main()
