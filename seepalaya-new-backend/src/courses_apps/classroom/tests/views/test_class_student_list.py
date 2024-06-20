import json
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch
from django.core.exceptions import ValidationError as DjangoValidationError
from courses_apps.classroom.models import ClassRoom
from courses_apps.teacher.selectors import teacher_get_from_user
from courses_apps.learner.models import Learner
from django.contrib.auth import get_user_model

User = get_user_model()

class ClassStudentListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.class_student_list_uri = reverse('classroom:get_classroom_students')
        self.teacher_signup_uri = reverse('teacher:teacher_signup')
        self.learner_signup_uri = reverse('learner:learner_signup')
        self.teacher_student_creation_uri = reverse('classroom:student_create')

        # Create teacher account and classroom
        teacher_signup_data = {
            'full_name': 'Test Teacher',
            'email': 'test_teacher@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        teacher_signup_response = self.client.post(self.teacher_signup_uri, teacher_signup_data)
        self.assertEqual(teacher_signup_response.status_code, 201)
        self.teacher_access_token = teacher_signup_response.data['data']['access_token']
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


    def create_students_through_api(self, class_code, students):
        """
        Helper function to create students through TeacherStudentCreationAPIView.
        Returns the response data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        request_data = {
            'class_code': class_code,
            'students': students
        }
        response = self.client.post(self.teacher_student_creation_uri, request_data, format='json')
        return response.data

    @patch('courses_apps.classroom.selectors.get_classroom_students')
    def test_get_classroom_students_after_creation(self, mock_get_classroom_students):
        """Test retrieving the list of students in a classroom after creating students."""
        # Mock data returned by get_classroom_students selector
        mock_get_classroom_students.return_value = [
            {'full_name': 'Student One', 'username': 'student1'},
            {'full_name': 'Student Two', 'username': 'student2'},
            {'full_name': 'Student Three', 'username': 'student3'}
        ]

        # Create students through TeacherStudentCreationAPIView
        students_to_create = ['Student Two', 'Student Three', 'Student One']
        creation_response_data = self.create_students_through_api(self.classroom.class_code, students_to_create)

        # Retrieve the list of students using ClassStudentListAPIView
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        request_data = {'class_code': self.classroom.class_code}
        response = self.client.post(self.class_student_list_uri, request_data, format='json')

        # Ensure the response content type is JSON
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()  # Parse JSON response

        # Check the structure and content of the response
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], "Students fetched successfully.")

        # Compare the students created through API with the students fetched from the classroom
        self.assertEqual(len(response_data['data']), len(mock_get_classroom_students.return_value))

        expected_full_names = {student['full_name'] for student in mock_get_classroom_students.return_value}
        retrieved_full_names = {student['full_name'] for student in response_data['data']}

        self.assertEqual(expected_full_names, retrieved_full_names)

    @patch('courses_apps.classroom.selectors.get_classroom_students')
    def test_get_classroom_students_invalid_class_code(self, mock_get_classroom_students):
        """Test retrieving students with an invalid class code."""
        mock_get_classroom_students.side_effect = DjangoValidationError("Classroom does not exist.")

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        request_data = {'class_code': 'INVALID_CODE'}
        response = self.client.post(self.class_student_list_uri, request_data, format='json')

        # Ensure the response content type is JSON
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()  # Parse JSON response
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], "Classroom does not exist.")

    def test_get_classroom_students_missing_class_code(self):
        """Test that missing class code returns a specific error message."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        request_data = {}
        response = self.client.post(self.class_student_list_uri, request_data, format='json')

        # Ensure the response content type is JSON
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()  # Parse JSON response

        # Check the specific error message for missing class_code field
        self.assertEqual(response_data['class_code'][0], "This field is required.")

    def test_get_classroom_students_unauthenticated(self):
        """Test that an unauthenticated request returns 401 Unauthorized."""
        request_data = {'class_code': 'TC123'}
        response = self.client.post(self.class_student_list_uri, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('courses_apps.classroom.selectors.get_classroom_students')
    def test_get_classroom_students_by_learner(self, mock_get_classroom_students):
        """Test retrieving students with an invalid class code."""
        mock_get_classroom_students.side_effect = DjangoValidationError("Classroom does not exist.")

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.learner_access_token)
        request_data = {'class_code': 'TC123'}
        response = self.client.post(self.class_student_list_uri, request_data, format='json')

        # Ensure the response content type is JSON
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response_data = response.json()  # Parse JSON response
        self.assertEqual(response_data['detail'], "You do not have permission to perform this action.")
