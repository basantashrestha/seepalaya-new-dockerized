import os
import csv
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import default_storage
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from courses_apps.teacher.models import Teacher
from courses_apps.classroom.models import ClassRoom
from courses_apps.teacher.selectors import teacher_get_from_user
from courses_apps.classroom.selectors import get_class_room_name_from_class_code
from courses_apps.classroom.services import student_create
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class TeacherStudentCreationAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher_student_creation_uri = reverse('classroom:student_create')
        self.teacher_signup_uri = reverse('teacher:teacher_signup')
        self.learner_signup_uri = reverse('learner:learner_signup')

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

    @patch('courses_apps.classroom.selectors.get_class_room_name_from_class_code')
    @patch('courses_apps.classroom.services.student_create')
    def test_teacher_student_creation_success(self, mock_student_create, mock_get_class_room_name_from_class_code):
        """Test successful creation of students by the teacher."""
        mock_student_create.return_value = [{'username': 'student1', 'full_name': 'Student One', 'password': 'password1'}]
        mock_get_class_room_name_from_class_code.return_value = 'Test Classroom'

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        student_data = {
            'class_code': 'TC123',
            'students': ['Student Test One']
        }
        response = self.client.post(self.teacher_student_creation_uri, student_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], "Students added successfully")
        self.assertEqual(response.data['data']['students'][0]['full_name'], 'Student Test One')
        self.assertEqual(response.data['class_name'], 'Test Classroom')
        self.assertIn('file_url', response.data)

    def test_teacher_student_creation_unauthenticated(self):
        """Test that an unauthenticated user cannot create students."""
        student_data = {
            'class_code': 'TC123',
            'students': ['Student Test']
        }
        response = self.client.post(self.teacher_student_creation_uri, student_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teacher_student_creation_forbidden(self):
        """Test that an authenticated learner cannot create students."""
        learner_signup_data = {
            'full_name': 'Test Learner',
            'email': 'test_learner@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        learner_signup_response = self.client.post(self.learner_signup_uri, learner_signup_data)
        self.assertEqual(learner_signup_response.status_code, 201)
        learner_access_token = learner_signup_response.data['data']['access_token']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + learner_access_token)
        student_data = {
            'class_code': 'TC123',
            'students': ['student1@test.com']
        }
        response = self.client.post(self.teacher_student_creation_uri, student_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_student_creation_invalid_input(self):
        """Test that invalid input returns a 400 error."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        student_data = {
            'class_code': '',
            'students': []
        }
        response = self.client.post(self.teacher_student_creation_uri, student_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('courses_apps.classroom.selectors.get_class_room_name_from_class_code')
    @patch('courses_apps.classroom.services.student_create')
    def test_teacher_student_creation_file_created(self, mock_student_create, mock_get_class_room_name_from_class_code):
        """Test that CSV file is created and contains correct data."""
        mock_student_create.return_value = [{'username': 'student1', 'full_name': 'Student One', 'password': 'password1'}]
        mock_get_class_room_name_from_class_code.return_value = 'Test Classroom'

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        student_data = {
            'class_code': 'TC123',
            'students': ['Student One']
        }
        response = self.client.post(self.teacher_student_creation_uri, student_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        csv_file_path = os.path.join(settings.MEDIA_ROOT, f'created_students_{self.teacher_user.username}.csv')
        self.assertTrue(os.path.exists(csv_file_path))

        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['full_name'], 'Student One')
        
        # Clean up the file
        os.remove(csv_file_path)
