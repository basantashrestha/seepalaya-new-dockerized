from unittest.mock import patch, Mock
from django.urls import reverse
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.test import APIClient, APITestCase
from django.db import connection, connections
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateClassRoomAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.uri = reverse('classroom:create_classroom')
        self.teacher_signup_uri = reverse('teacher:teacher_signup')
        self.learner_signup_uri = reverse('learner:learner_signup')

        teacher_signup_data = {
            'full_name': 'Test Teacher',
            'email': 'test_teacher@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        teacher_signup_response = self.client.post(self.teacher_signup_uri, teacher_signup_data)
        print("Teacher Signup Response:", teacher_signup_response.content)
        self.assertEqual(teacher_signup_response.status_code, 201)
        # Extract the access token from the response
        self.teacher_access_token = teacher_signup_response.data['data']['access_token']

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

    @patch('courses_apps.classroom.services.create_classroom')
    def test_create_classroom_success(self, mock_create_classroom):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')
        mock_create_classroom.return_value = Mock(title='Test Classroom')
        response = self.client.post(self.uri, {'title': 'Test Classroom'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Classroom created successfully.')

    @patch('courses_apps.classroom.services.create_classroom')
    def test_create_classroom_invalid_data(self, mock_create_classroom):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')
        mock_create_classroom.side_effect = DjangoValidationError('Invalid data')
        response = self.client.post(self.uri, {'title': ''})
        self.assertEqual(response.status_code, 400)

    @patch('courses_apps.classroom.services.create_classroom')
    def test_create_classroom_missing_data(self, mock_create_classroom):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')
        mock_create_classroom.side_effect = DjangoValidationError('Missing data')
        response = self.client.post(self.uri, {})
        self.assertEqual(response.status_code, 400)

    def test_create_classroom_as_learner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.learner_access_token}')
        response = self.client.post(self.uri, {'title': 'Test Classroom'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
