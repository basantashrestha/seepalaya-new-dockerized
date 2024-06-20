from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from unittest.mock import patch, MagicMock
from courses_apps.account.models import EmailConfirmationToken
from courses_apps.account.services import confirmation_email_resend
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

class ConfirmationEmailResendTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='strongpass@123'
        )

    @patch('courses_apps.account.selectors.email_confirmation_token_get_from_user')
    def test_confirmation_email_resend_no_email(self, mock_email_confirmation_token_get_from_user):
        mock_email_confirmation_token_get_from_user.return_value = None
        # Directly test for ValidationError without saving the user with a None email
        self.user.email = None

        with self.assertRaises(ValidationError) as context:
            confirmation_email_resend(user=self.user)

        self.assertEqual(str(context.exception.detail[0]), _('User does not have an email.'))

    def test_confirmation_email_resend_verified_user(self):
        self.user.is_verified = True

        with self.assertRaises(ValidationError) as context:
            confirmation_email_resend(user=self.user)

        self.assertEqual(str(context.exception.detail[0]), _('User already verified'))
