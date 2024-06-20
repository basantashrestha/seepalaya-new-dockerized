import unittest
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.test import TestCase

class TestUserLoginAPIView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.learner_signup_uri = reverse('learner:learner_signup')
        
        learner_signup_data = {
            'full_name': 'Test Learner',
            'email': 'test_learner@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        learner_signup_response = self.client.post(self.learner_signup_uri, learner_signup_data)
        print("Learner Signup Response:", learner_signup_response.content)
        self.assertEqual(learner_signup_response.status_code, 201)
        self.learner_access_token = learner_signup_response.data['data']['access_token']

    def test_successful_user_login(self):
        url = reverse('account:login')
        data = {
            'username_or_email': 'testuser',
            'password': 'password123'
        }
        with patch('courses_apps.account.services.user_login') as mocked_user_login, \
                patch.object(APIClient, 'post') as mocked_post:
            mocked_user_login.return_value = (MagicMock(), 'mocked_refresh_token')
            mocked_post.return_value = MagicMock(
                status_code=status.HTTP_200_OK, 
                data={'success': True, 'data': {'access_token': 'mocked_access_token'}}
            )
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertIn('data', response.data)
        self.assertTrue('access_token' in response.data['data'])

    def test_invalid_credentials(self):
        url = reverse('account:login')
        data = {
            'username_or_email': 'testuser',
            'password': 'invalidpassword'
        }
        with patch('courses_apps.account.services.user_login') as mocked_user_login:
            mocked_user_login.side_effect = ValidationError('Invalid credentials')
            
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data.get('success'))
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid credentials.')

    def test_missing_input_data(self):
        url = reverse('account:login')
        data = {}  # Missing required fields
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))
        self.assertIn('username_or_email', response.data)
        self.assertIn('password', response.data)

    def test_empty_input_data(self):
        url = reverse('account:login')
        data = {}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))
        self.assertIn('username_or_email', response.data)
        self.assertIn('password', response.data)


    def test_invalid_input_data_types(self):
        url = reverse('account:login')
        data = {
            'username_or_email': 'testuser',
            'password': 123
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data.get('success'))
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'].code, 'invalid')

    def test_unexpected_error_in_login_service(self):
        url = reverse('account:login')
        data = {
            'username_or_email': 'testuser',
            'password': 'password123'
        }
        with patch('courses_apps.account.services.user_login') as mocked_user_login:
            mocked_user_login.side_effect = Exception('Unexpected error')
            
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data.get('success'))
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'].code, 'invalid')

if __name__ == '__main__':
    import django
    django.setup()
    TestCase.main()
