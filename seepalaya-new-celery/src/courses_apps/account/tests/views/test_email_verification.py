from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from courses_apps.account.models import EmailConfirmationToken
import uuid
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class UserEmailVerificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher_signup_uri = reverse('teacher:teacher_signup')
        self.learner_signup_uri = reverse('learner:learner_signup')
        self.email_verification_uri = reverse('account:user_email_conmfirmation')

        # Signup data for a new teacher
        self.teacher_signup_data = {
            'full_name': 'Test Teacher',
            'email': 'test_teacher@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }

        self.learner_signup_data = {
            'full_name': 'Test Learner',
            'email': 'test_learner@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }

    def test_email_confirmation(self):
        signup_response = self.client.post(self.teacher_signup_uri, self.teacher_signup_data)
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.teacher_signup_data['email'])

        # Fetch the automatically generated confirmation token
        email_confirmation_token = EmailConfirmationToken.objects.get(user=user)
        token = email_confirmation_token.token

        # Verify email using the token
        email_verification_data = {
            'token': token
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + signup_response.data['data']['access_token'])
        verification_response = self.client.post(self.email_verification_uri, email_verification_data)
        
        # Check the response and user's verified status
        self.assertEqual(verification_response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_email_confirmation_with_invalid_token(self):
        signup_response = self.client.post(self.teacher_signup_uri, self.teacher_signup_data)
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.teacher_signup_data['email'])

        invalid_token = 'invalidtoken123'
        email_verification_data = {
            'token': invalid_token
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + signup_response.data['data']['access_token'])
        verification_response = self.client.post(self.email_verification_uri, email_verification_data)
        
        self.assertEqual(verification_response.status_code, status.HTTP_403_FORBIDDEN)
        user.refresh_from_db()
        self.assertFalse(user.is_verified)

    def test_email_confirmation_with_expired_token(self):
        signup_response = self.client.post(self.learner_signup_uri, self.learner_signup_data)
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.learner_signup_data['email'])

        # Fetch the automatically generated confirmation token
        email_confirmation_token = EmailConfirmationToken.objects.get(user=user)

        # Simulate token expiration by setting the created_time in the past
        expired_time = timezone.now() - timedelta(minutes=15)
        
        # Temporarily disable auto_now behavior
        email_confirmation_token._meta.get_field('created_time').auto_now = False
        email_confirmation_token.created_time = expired_time
        email_confirmation_token.save(update_fields=['created_time'])
        email_confirmation_token._meta.get_field('created_time').auto_now = True

        token = email_confirmation_token.token

        # Verify email using the expired token
        email_verification_data = {
            'token': token
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + signup_response.data['data']['access_token'])
        verification_response = self.client.post(self.email_verification_uri, email_verification_data)
        
        self.assertEqual(verification_response.status_code, status.HTTP_403_FORBIDDEN)
        user.refresh_from_db()
        self.assertFalse(user.is_verified)
        self.assertIn("Confirmation email has expired.", verification_response.data['message'])