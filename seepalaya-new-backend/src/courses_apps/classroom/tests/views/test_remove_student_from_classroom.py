from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from courses_apps.teacher.models import Teacher
from courses_apps.classroom.models import ClassRoom
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()

class AddStudentsToClassRoomAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher_student_removal_uri = reverse('classroom:remove_student_from_classroom')
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
        self.classroom.students.add(self.learner1_user, self.learner2_user)
        self.classroom.save()

    @patch('courses_apps.classroom.services.remove_students_from_classroom')
    def test_remove_student_from_classroom_success(self, mock_student_remove):
        mock_student_remove.return_value = True
        data = {
            'class_code':'TC123', 
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_removal_uri, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Students removed successfully.')
    
    def test_remove_student_from_classroom_missing_fields(self):
        data = {
            'class_code':'TC123'
        }
        response = self.client.post(self.teacher_student_removal_uri, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['students'][0], "This field is required.")
    
    def test_remove_student_from_classroom_invalid_class_code(self):
        data = {
            'class_code':'TC1234', 
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_removal_uri, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Classroom does not exist.')

    def test_student_remove_from_classroom_unauthenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='')
        data = {
            'class_code':'TC123', 
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_removal_uri, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_remove_from_classroom_permission_denied_to_classroom(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.second_teacher_access_token)
        data = {
            'class_code': 'TC123',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_removal_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Teacher is not the owner of the classroom.')

    def test_student_remove_from_classroom_permission_denied(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.second_teacher_access_token)
        data = {
            'class_code': 'TC127',
            'students': [self.learner1_user.username, self.learner2_user.username]
        }
        response = self.client.post(self.teacher_student_removal_uri, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'The user is not a student of the teacher.')
