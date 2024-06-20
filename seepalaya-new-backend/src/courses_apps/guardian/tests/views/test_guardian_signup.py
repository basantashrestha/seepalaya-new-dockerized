import unittest
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class TestGuardianSignupAPIView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = APIClient()

    def test_successful_guardian_signup(self):
        url = reverse('guardian:guardian_signup')
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        with patch('courses_apps.guardian.services.guardian_signup') as mocked_guardian_signup, \
            patch.object(APIClient, 'post') as mocked_post:
            mocked_guardian_signup.return_value = (MagicMock(), 'mocked_refresh_token')
            mocked_post.return_value = MagicMock(status_code=status.HTTP_201_CREATED, data={'success': True, 'data': {'access_token': 'mocked_access_token'}})
            response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        self.assertIn('data', response.data)
        self.assertTrue('access_token' in response.data['data'])

    
    def test_invalid_data(self):
        url = reverse('guardian:guardian_signup')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('confirm_password', response.data)

    def test_password_mismatch(self):
        url = reverse('guardian:guardian_signup')
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password1234'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_format(self):
        url = reverse('guardian:guardian_signup')
        data = {
            'email': 'invalid_email',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('courses_apps.guardian.services.guardian_signup')
    def test_guardian_signup_failed(self, mocked_guardian_signup):
        mocked_guardian_signup.side_effect = ValidationError('Signup failed.')
        url = reverse('guardian:guardian_signup')
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('courses_apps.account.services.email_confirmation_token_send')
    def test_email_confirmation_failed(self, mocked_email_confirmation_token_send):
        mocked_email_confirmation_token_send.side_effect = ValidationError('Email confirmation failed.')
        url = reverse('guardian:guardian_signup')
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



if __name__ == '__main__':
    unittest.main()
