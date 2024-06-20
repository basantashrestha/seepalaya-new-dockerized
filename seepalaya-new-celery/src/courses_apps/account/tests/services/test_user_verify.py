from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from datetime import timedelta
from courses_apps.account.models import EmailConfirmationToken
from courses_apps.account.services import user_verify
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

User = get_user_model()

class UserVerifyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='strongpass@123',
        )

    def create_token(self, minutes_offset=0):
        # Temporarily disable auto_now
        original_auto_now = EmailConfirmationToken._meta.get_field('created_time').auto_now
        EmailConfirmationToken._meta.get_field('created_time').auto_now = False

        # Create token with specified created_time
        try:
            created_time = timezone.now() + timedelta(minutes=minutes_offset)
            token = EmailConfirmationToken.objects.create(
                user=self.user,
                token='valid_token',
                email=self.user.email,
                created_time=created_time  # Explicitly set created_time
            )
        finally:
            # Restore original auto_now value
            EmailConfirmationToken._meta.get_field('created_time').auto_now = original_auto_now

        return token

    def test_valid_token_verification(self):
        token = self.create_token()
        verified_user = user_verify(user=self.user, token='valid_token')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertEqual(verified_user, self.user)
        self.assertFalse(EmailConfirmationToken.objects.filter(pk=token.pk).exists())

    def test_invalid_token_handling(self):
        with self.assertRaises(ValidationError) as context:
            user_verify(user=self.user, token='invalid_token')
        self.assertEqual(str(context.exception.detail[0]), str(_("Confirmation link is invalid.")))

    def test_expired_token_handling(self):
        token = self.create_token(minutes_offset=-15)
        with self.assertRaises(ValidationError) as context:
            user_verify(user=self.user, token='valid_token')
        self.assertEqual(str(context.exception.detail[0]), str(_("Confirmation email has expired. Please request a new confirmation email.")))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)