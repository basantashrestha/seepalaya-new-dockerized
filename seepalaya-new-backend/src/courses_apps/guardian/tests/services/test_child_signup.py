from django.test import TestCase
from rest_framework.exceptions import ValidationError
from datetime import date
from courses_apps.guardian.services import child_signup, guardian_signup
from django.contrib.auth import get_user_model

User = get_user_model()

class TestChildSignup(TestCase):
    def setUp(self):
        email = "guardian@example.com"
        password = "validpassword123"
        confirm_password = "validpassword123"

        signup_details, _ = guardian_signup(
            email=email,
            password=password,
            confirm_password=confirm_password
        )
        self.guardian_username = signup_details.username
        self.guardian_user = User.objects.get(username=self.guardian_username)


    def test_child_signup_invalid_guardian(self):
        with self.assertRaises(ValidationError) as context:
            child_signup(
                guardian_user=User.objects.create(username="another_guardian", email="another@example.com"),
                full_name="Child Name",
                username="child_username",
                pin="validpassword123",
                confirm_pin="validpassword123",
                date_of_birth=date(2010, 1, 1),
            )

        self.assertIn("Guardian does not exist.", str(context.exception))

    def test_child_signup_success(self):
        self.assertTrue(User.objects.filter(username=self.guardian_username).exists())

        signup_details = child_signup(
            guardian_user=self.guardian_user,
            full_name="Child Name",
            username="child_username",
            pin="validpassword123",
            confirm_pin="validpassword123",
            date_of_birth=date(2010, 1, 1),
        )

        self.assertEqual(signup_details.user_type, "learner")
        self.assertEqual(signup_details.username, "child_username")
        self.assertEqual(signup_details.full_name, "Child Name")
        self.assertEqual(signup_details.guardian_email, "guardian@example.com")
        self.assertEqual(signup_details.user_email, "child_username@example.com")
        self.assertTrue(signup_details.is_verified)  # Corrected assertion

    def test_child_signup_pin_too_short(self):

        self.assertTrue(User.objects.filter(username=self.guardian_username).exists())


        with self.assertRaises(ValidationError) as context:
            child_signup(
                guardian_user=self.guardian_user,
                full_name="Child Name",
                username="child_username",
                pin="12345",
                confirm_pin="12345",
                date_of_birth=date(2010, 1, 1),
            )
        
        self.assertEqual(context.exception.detail[0], "Pin must be at least 6 characters long.")
