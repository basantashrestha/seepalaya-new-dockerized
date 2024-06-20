from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from courses_apps.classroom.models import ClassRoom
from django.contrib.auth import get_user_model
from courses_apps.teacher.selectors import teacher_get_from_user

User = get_user_model()
class GetClassRoomListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_classroom_list_uri = reverse('teacher:classroom_list')
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

        # Create learner account
        learner_signup_data = {
            'full_name': 'Test Learner',
            'email': 'test_learner@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        learner_signup_response = self.client.post(self.learner_signup_uri, learner_signup_data)
        self.assertEqual(learner_signup_response.status_code, 201)
        self.learner_access_token = learner_signup_response.data['data']['access_token']

        # Create a classroom for the teacher
        self.classroom = ClassRoom.objects.create(
            title="Test Classroom",
            class_code="TC123",
            teacher=self.teacher_instance
        )
        self.classroom.students.add(User.objects.get(email='test_learner@gmail.com'))
        self.classroom.save()

    def test_get_classroom_list_authenticated_teacher(self):
        """Test that an authenticated teacher can get the list of classrooms."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)
        response = self.client.post(self.get_classroom_list_uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], "Classes fetched successfully.")
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['classroom_title'], "Test Classroom")

    def test_get_classroom_list_unauthenticated_user(self):
        """Test that an unauthenticated user cannot get the list of classrooms."""
        response = self.client.post(self.get_classroom_list_uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_classroom_list_authenticated_learner(self):
        """Test that an authenticated learner cannot get the list of classrooms."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.learner_access_token)
        response = self.client.post(self.get_classroom_list_uri)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_classroom_list_invalid_token(self):
        """Test that an invalid token results in authentication failure."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        response = self.client.post(self.get_classroom_list_uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_classroom_list_no_classrooms(self):
        """Test that a teacher with no classrooms gets an empty list."""
        # Create another teacher without classrooms
        another_teacher_signup_data = {
            'full_name': 'Another Teacher',
            'email': 'another_teacher@gmail.com',
            'password': 'strongpass@123',
            'confirm_password': 'strongpass@123'
        }
        another_teacher_signup_response = self.client.post(self.teacher_signup_uri, another_teacher_signup_data)
        self.assertEqual(another_teacher_signup_response.status_code, 201)
        another_teacher_access_token = another_teacher_signup_response.data['data']['access_token']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + another_teacher_access_token)
        response = self.client.post(self.get_classroom_list_uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], "Classes fetched successfully.")
        self.assertEqual(len(response.data['data']), 0)