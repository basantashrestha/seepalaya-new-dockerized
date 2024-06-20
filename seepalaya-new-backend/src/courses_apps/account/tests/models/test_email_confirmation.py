from datetime import timedelta
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from courses_apps.account.models import PortalUser, ProfilePicture, UserRoles, EmailConfirmationToken

class EmailConfirmationTokenModelTests(TestCase):

    def setUp(self):
        self.profile_picture = ProfilePicture.objects.create(
            link="http://example.com/image.jpg"
        )

        self.user = PortalUser.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            full_name="User One",
            profile_picture=self.profile_picture
        )

        self.token = EmailConfirmationToken.objects.create(
            user=self.user,
            token="1234567890abcdef1234567890abcdef",
            email="user1@example.com"
        )

    def test_token_creation(self):
        self.assertEqual(self.token.user, self.user)
        self.assertEqual(self.token.token, "1234567890abcdef1234567890abcdef")
        self.assertEqual(self.token.email, "user1@example.com")

    def test_string_representation(self):
        self.assertEqual(str(self.token), "user1user1@example.com")

    def test_verbose_name(self):
        self.assertEqual(EmailConfirmationToken._meta.verbose_name, "Email Confirmation Token")
        self.assertEqual(EmailConfirmationToken._meta.verbose_name_plural, "Email Confirmation Tokens")

    def test_ordering(self):
        self.assertEqual(EmailConfirmationToken._meta.ordering, ["-created_time"])
