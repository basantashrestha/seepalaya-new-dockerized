import json
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from courses_apps.classroom.models import ClassRoom
from courses_apps.teacher.models import Teacher
from courses_apps.learner.models import Learner
from courses_apps.teacher.selectors import teacher_get_from_user
from courses_apps.classroom.services import join_classroom
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()

class JoinClassRoomWithCodeAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.join_classroom_uri = reverse('classroom:join_classroom')
        self.teacher_signup_uri = reverse('teacher:teacher_signup')
        self.learner_signup_uri = reverse('learner:learner_signup')

        # Create teacher account and classroom
        teacher_signup_data = {
            'full_name': 'Test Teacher',
            'email': 'test_teacher@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        teacher_signup_response = self.client.post(self.teacher_signup_uri, teacher_signup_data)
        self.assertEqual(teacher_signup_response.status_code, 201)
        self.teacher_user = User.objects.get(email='test_teacher@gmail.com')
        self.teacher_instance = teacher_get_from_user(user=self.teacher_user)

        self.classroom = ClassRoom.objects.create(
            title="Test Classroom",
            class_code="TC123",
            teacher=self.teacher_instance
        )

        # Create learner account and authenticate
        learner_signup_data = {
            'full_name': 'Test Learner',
            'email': 'test_learner@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        learner_signup_response = self.client.post(self.learner_signup_uri, learner_signup_data)
        self.assertEqual(learner_signup_response.status_code, 201)
        self.learner_access_token = learner_signup_response.data['data']['access_token']
        self.learner_user = User.objects.get(email='test_learner@gmail.com')

    @patch('courses_apps.classroom.services.join_classroom')
    def test_join_classroom_success(self, mock_join_classroom):
        """Test successful joining of a classroom with a valid class code."""
        mock_join_classroom.return_value = {
            'class_code': 'TC123',
            'title': 'Test Classroom',
            'student_count': 1
        }

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.learner_access_token)
        join_data = {'class_code': 'TC123'}
        response = self.client.post(self.join_classroom_uri, join_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['content-type'], 'application/json')
        
        response_data = response.json()

        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], "Classroom joined successfully.")
        self.assertEqual(response_data['data'], 'Test Classroom')
    
    @patch('courses_apps.classroom.services.join_classroom')
    def test_join_classroom_student_already_in_class(self, mock_join_classroom):
        """Test joining a classroom when the student is already in the class."""
        # First attempt to join the class (successful)
        successful_join_response_data = self.test_join_classroom_success()

        # Modify mock to simulate student already in the class
        mock_join_classroom.side_effect = ValueError("Student is already in the classroom.")

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.learner_access_token)
        join_data = {'class_code': 'TC123'}
        response = self.client.post(self.join_classroom_uri, join_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['content-type'], 'application/json')

        response_data = response.json()

        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], "Student is already in the classroom.")


    def test_join_classroom_unauthenticated(self):
        """Test that an unauthenticated user cannot join a classroom."""
        join_data = {'class_code': 'TC123'}
        response = self.client.post(self.join_classroom_uri, join_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('courses_apps.classroom.services.join_classroom')
    def test_join_classroom_invalid_class_code(self, mock_join_classroom):
        """Test joining a classroom with an invalid class code."""
        mock_join_classroom.side_effect = DjangoValidationError("Classroom does not exist.")

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.learner_access_token)
        join_data = {'class_code': 'INVALID_CODE'}
        response = self.client.post(self.join_classroom_uri, join_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], "Classroom does not exist.")

    def test_join_classroom_missing_class_code(self):
        """Test that missing class code returns a 400 error."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.learner_access_token)
        join_data = {}
        response = self.client.post(self.join_classroom_uri, join_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
