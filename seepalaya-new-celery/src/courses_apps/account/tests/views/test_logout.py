import threading
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserLogoutAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@gmail.com', password='testpassword')
        self.refresh_token = str(RefreshToken.for_user(self.user))
        self.logout_url = reverse('account:logout')

    def test_successful_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(self.logout_url, {}, HTTP_COOKIE=f"refresh_token={self.refresh_token}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_refresh_token(self):
        self.client.force_login(self.user)
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_refresh_token(self):
        self.client.force_login(self.user)
        invalid_refresh_token = "invalid_token"
        response = self.client.post(self.logout_url, {}, HTTP_COOKIE=f"refresh_token={invalid_refresh_token}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_when_already_logged_out(self):
        self.client.force_login(self.user)
        refresh_token = str(RefreshToken.for_user(self.user))
        self.client.post(self.logout_url, {}, HTTP_COOKIE=f"refresh_token={refresh_token}")
        response = self.client.post(self.logout_url, {}, HTTP_COOKIE=f"refresh_token={refresh_token}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_logout(self):
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
