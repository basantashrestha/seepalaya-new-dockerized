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

class AddStudentsToClassRoomAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher_student_add_uri = reverse('classroom:add_student_to_classroom')
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
        self.teacher_instance = Teacher.objects.get(user=self.teacher_user)

        # Create a classroom for the teacher
        self.classroom = ClassRoom.objects.create(
            title="Test Classroom",
            class_code="TC123",
            teacher=self.teacher_instance
        )

        # Authenticate as the teacher for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)

        # Create learner accounts
        learner1_signup_data = {
            'full_name': 'Test Learner One',
            'email': 'test_learner1@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        learner2_signup_data = {
            'full_name': 'Test Learner Two',
            'email': 'test_learner2@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }

        learner1_signup_response = self.client.post(self.learner_signup_uri, learner1_signup_data)
        self.assertEqual(learner1_signup_response.status_code, 201)

        learner2_signup_response = self.client.post(self.learner_signup_uri, learner2_signup_data)
        self.assertEqual(learner2_signup_response.status_code, 201)

        self.learner1_user = User.objects.get(email='test_learner1@gmail.com')
        self.learner2_user = User.objects.get(email='test_learner2@gmail.com')

        # Add learners to teacher's students
        self.teacher_instance.students.add(self.learner1_user, self.learner2_user)

        second_teacher_signup_data = {
            'full_name': 'Test Teacher Two',
            'email': 'test_teacher_two@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        second_teacher_signup_response = self.client.post(self.teacher_signup_uri, second_teacher_signup_data)
        self.assertEqual(second_teacher_signup_response.status_code, 201)
        self.second_teacher_access_token = second_teacher_signup_response.data['data']['access_token']
        self.second_teacher_user = User.objects.get(email='test_teacher_two@gmail.com')
        self.second_teacher_instance = Teacher.objects.get(user=self.second_teacher_user)

        # Create a classroom for the second teacher
        self.classroom = ClassRoom.objects.create(
            title="Test Classroom",
            class_code="TC127",
            teacher=self.second_teacher_instance
        )
                                                    

    def test_add_students_to_classroom_success(self):
        data = {
            'class_code': 'TC123',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertIn('Students added successfully', response.data['message'])

    def test_add_students_to_classroom_missing_fields(self):
        data = {
            'class_code': 'TC123'
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['students'][0], "This field is required.")

    def test_add_students_to_classroom_invalid_class_code(self):
        data = {
            'class_code': 'INVALID123',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)

    def test_add_students_to_classroom_unauthenticated(self):
        self.client.credentials()
        data = {
            'class_code': 'TC123',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_students_to_classroom_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        data = {
            'class_code': 'TC123',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_students_to_classroom_permission_denied_to_classroom(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.second_teacher_access_token)
        data = {
            'class_code': 'TC123',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Teacher is not the owner of the classroom.')

    def test_add_students_to_classroom_permission_denied(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.second_teacher_access_token)
        data = {
            'class_code': 'TC127',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_add_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'The user is not a student of the teacher.')