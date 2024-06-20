from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.views import Response
from rest_framework import status
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses_apps.account.views import ChangePasswordAPIView
from django.urls import reverse

User = get_user_model()

class ChangePasswordAPIViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.view = ChangePasswordAPIView.as_view()
        self.login_uri = reverse('account:login')
        self.change_password_uri = reverse('account:change_password')
        self.user = User.objects.create_user(username='test_user', email='testuser@email.com', password='old_password', full_name='Test User')

        login_data = {'username_or_email': 'test_user', 'password': 'old_password'}
        login_response = self.client.post(self.login_uri, login_data, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.access_token = login_response.data['data']['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_change_password_success(self):
        data = {
            'old_password': 'old_password',
            'new_password': 'strongpass@123'
        }
        response = self.client.post(self.change_password_uri, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], "Password changed successfully.")

        # Verify that the password has actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('strongpass@123'))

    def test_change_password_validation_error(self):
        data = {
            'old_password': 'wrong_password',  # incorrect old password
            'new_password': 'new_password123'
        }
        response = self.client.post(self.change_password_uri, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('Old password is incorrect.', response.data['message'])

    def test_change_password_missing_fields(self):
        data = {
            'old_password': 'old_password'
        }
        response = self.client.post(self.change_password_uri, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'][0], 'This field is required.')
    
    def test_change_password_invalid_new_password(self):
        data = {
            'old_password': 'old_password',
            'new_password': '123'  # new password too short
        }
        response = self.client.post(self.change_password_uri, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'This password is too short. It must contain at least 8 characters.')

    def test_change_password_missing_old_password(self):
        data = {
            'new_password': 'new_password123'
        }
        response = self.client.post(self.change_password_uri, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['old_password'][0], 'This field is required.')
