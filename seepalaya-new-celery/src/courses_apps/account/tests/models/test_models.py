from django.test import TestCase
from django.contrib.auth import get_user_model
from courses_apps.account.models import ProfilePicture, UserRoles

User = get_user_model()

class UserManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', username='user', password='password123')

    def test_create_user(self):
        self.assertEqual(self.user.email, 'user@test.com')
        self.assertEqual(self.user.username, 'user')
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(email='superuser@test.com', username='superuser', password='password123')
        self.assertEqual(superuser.email, 'superuser@test.com')
        self.assertEqual(superuser.username, 'superuser')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

class ProfilePictureTestCase(TestCase):
    def setUp(self):
        self.profile_picture = ProfilePicture.objects.create(name='Profile Picture', link='http://example.com/picture.jpg')

    def test_profile_picture_creation(self):
        self.assertEqual(self.profile_picture.name, 'Profile Picture')
        self.assertEqual(self.profile_picture.link, 'http://example.com/picture.jpg')

class UserRolesTestCase(TestCase):
    def setUp(self):
        self.user_role = UserRoles.objects.create(name='Role', description='Role Description')

    def test_user_role_creation(self):
        self.assertEqual(self.user_role.name, 'Role')
        self.assertEqual(self.user_role.description, 'Role Description')

