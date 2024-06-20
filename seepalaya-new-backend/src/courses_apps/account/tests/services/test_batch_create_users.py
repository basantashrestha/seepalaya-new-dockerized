# from django.test import TestCase
# from django.core.exceptions import ValidationError as DjangoValidationError
# from unittest.mock import patch
# from concurrent.futures import ThreadPoolExecutor
# from courses_apps.account.models import UserRoles
# from courses_apps.account.services import batch_create_users
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class BatchCreateUsersTestCase(TestCase):

#     @patch('courses_apps.account.selectors.check_if_email_is_taken')
#     @patch('courses_apps.account.selectors.user_get_from_username')
#     @patch('courses_apps.account.selectors.get_user_role_by_name')
#     def test_batch_create_users_success(self, mock_get_user_role_by_name, mock_user_get_from_username, mock_check_if_email_is_taken):
#         # Mock the return values for the mocked functions
#         mock_check_if_email_is_taken.return_value = None
#         mock_user_get_from_username.return_value = None
#         mock_get_user_role_by_name.return_value = UserRoles.objects.create(name='student')

#         users_data = [
#             {'username': 'user1', 'email': 'user1@example.com', 'password': 'password1', 'user_type': 'student', 'full_name': 'User One'},
#             {'username': 'user2', 'email': 'user2@example.com', 'password': 'password2', 'user_type': 'student', 'full_name': 'User Two'}
#         ]

#         created_users = batch_create_users(users_data)

#         # Assert that users are created
#         self.assertEqual(len(created_users), 2)
#         self.assertTrue(all(isinstance(user, User) for user in created_users))

#         # Assert that usernames are lowercase
#         self.assertEqual(created_users[0].username, 'user1')
#         self.assertEqual(created_users[1].username, 'user2')

#     @patch('courses_apps.account.selectors.check_if_email_is_taken')
#     @patch('courses_apps.account.selectors.user_get_from_username')
#     @patch('courses_apps.account.selectors.get_user_role_by_name')
#     def test_batch_create_users_duplicate_email(self, mock_get_user_role_by_name, mock_user_get_from_username, mock_check_if_email_is_taken):
#         # Mock the return value for check_if_email_is_taken to simulate existing user
#         mock_check_if_email_is_taken.return_value = User.objects.create(username='existinguser', email='user1@example.com')

#         users_data = [
#             {'username': 'user1', 'email': 'user1@example.com', 'password': 'password1', 'user_type': 'student', 'full_name': 'User One'}
#         ]

#         with self.assertRaises(DjangoValidationError) as context_manager:
#             batch_create_users(users_data)

#         self.assertIn('User with the email already exists.', str(context_manager.exception))

#     @patch('courses_apps.account.selectors.check_if_email_is_taken')
#     @patch('courses_apps.account.selectors.user_get_from_username')
#     @patch('courses_apps.account.selectors.get_user_role_by_name')
#     def test_batch_create_users_duplicate_username(self, mock_get_user_role_by_name, mock_user_get_from_username, mock_check_if_email_is_taken):
#         # Mock the return value for user_get_from_username to simulate existing user
#         mock_user_get_from_username.return_value = User.objects.create(username='user1', email='existinguser@example.com')

#         users_data = [
#             {'username': 'user1', 'email': 'user1@example.com', 'password': 'password1', 'user_type': 'student', 'full_name': 'User One'}
#         ]

#         with self.assertRaises(DjangoValidationError) as context_manager:
#             batch_create_users(users_data)

#         self.assertIn('User with the username `user1` already exists.', str(context_manager.exception))

