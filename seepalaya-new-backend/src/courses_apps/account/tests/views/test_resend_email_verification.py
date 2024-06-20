from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError
from courses_apps.account.models import EmailConfirmationToken
from courses_apps.account.services import confirmation_email_resend
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()

class ResendEmailConfirmationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='strongpass@123'
        )
        self.resend_email_confirmation_uri = reverse('account:resend_email_confirmation')

    def test_resend_email_confirmation_success(self):
        self.client.force_authenticate(user=self.user)
        with patch('courses_apps.account.views.confirmation_email_resend') as mock_confirmation_email_resend:
            mock_confirmation_email_resend.return_value = EmailConfirmationToken(user=self.user, token='new_token')
            response = self.client.post(self.resend_email_confirmation_uri, {})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['success'], True)
            self.assertEqual(response.data['message'], 'Confirmation email resent successfully.')

    def test_resend_email_confirmation_validation_error(self):
        self.client.force_authenticate(user=self.user)
        with patch('courses_apps.account.views.confirmation_email_resend') as mock_confirmation_email_resend:
            mock_confirmation_email_resend.side_effect = ValidationError(detail="Some validation error")
            response = self.client.post(self.resend_email_confirmation_uri, {})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['success'], False)
            self.assertEqual(response.data['message'], 'Some validation error')

    def test_resend_email_confirmation_django_validation_error(self):
        self.client.force_authenticate(user=self.user)
        with patch('courses_apps.account.views.confirmation_email_resend') as mock_confirmation_email_resend:
            mock_confirmation_email_resend.side_effect = DjangoValidationError("Some Django validation error")
            response = self.client.post(self.resend_email_confirmation_uri, {})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['success'], False)
            self.assertEqual(response.data['message'], 'Some Django validation error')