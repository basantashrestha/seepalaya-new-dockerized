from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.test import APIClient, APITestCase
from django.db import connection, connections
from django.contrib.auth import get_user_model
from courses_apps.classroom.models import ClassRoom
from courses_apps.classroom.services import delete_classroom
from courses_apps.teacher.selectors import teacher_get_from_user

User = get_user_model()

class DeleteClassRoomAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.delete_classroom_uri = reverse('classroom:classroom_delete')
        self.teacher_signup_uri = reverse('teacher:teacher_signup')

        # Create teacher account and authenticate
        teacher_signup_data = {
            'full_name': 'Test Teacher',
            'email': 'test_teacher@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        teacher_signup_response = self.client.post(self.teacher_signup_uri, teacher_signup_data)
        self.assertEqual(teacher_signup_response.status_code, 201)
        self.teacher_access_token = teacher_signup_response.data['data']['access_token']
        
        # Get the teacher user and teacher instance
        self.teacher_user = User.objects.get(email='test_teacher@gmail.com')
        self.teacher_instance = teacher_get_from_user(user=self.teacher_user)

        # Create a classroom for the teacher
        self.classroom = ClassRoom.objects.create(
            title="Test Classroom",
            class_code="TC123",
            teacher=self.teacher_instance
        )
        self.classroom.save()

        # Create another teacher account
        second_teacher_signup_data = {
            'full_name': 'Test Teacher Two',
            'email': 'test_teacher_two@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        second_teacher_signup_response = self.client.post(self.teacher_signup_uri, second_teacher_signup_data)
        self.assertEqual(second_teacher_signup_response.status_code, 201)
        self.second_teacher_access_token = second_teacher_signup_response.data['data']['access_token']

    @patch('courses_apps.classroom.services.delete_classroom')
    def test_delete_classroom_success(self, mock_update_classroom):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')
        # mock_update_classroom.return_value = Mock(title='Test Classroom Updated')
        response = self.client.post(self.delete_classroom_uri, {'class_code':'TC123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Classroom deleted successfully.')

    def test_get_classroom_list_unauthenticated_user(self):
        """Test that an unauthenticated user cannot get the list of classrooms."""
        response = self.client.get(self.delete_classroom_uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_classroom_list_invalid_token(self):
        """Test that an invalid token results in authentication failure."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        response = self.client.get(self.delete_classroom_uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_classroom_invalid_class_code(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')
        response = self.client.post(self.delete_classroom_uri, {'class_code':'TC1234', 'title': 'Test Classroom Updated'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Classroom does not exist.')
    
    def test_update_classroom_unauthorized_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.second_teacher_access_token}')
        response = self.client.post(self.delete_classroom_uri, {'class_code':'TC123', 'title': 'Test Classroom Updated'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Teacher is not the owner of the classroom.')
