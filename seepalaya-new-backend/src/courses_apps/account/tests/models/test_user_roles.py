from django.test import TestCase
from courses_apps.account.models import UserRoles

class UserRolesTestCase(TestCase):
    def setUp(self):
        self.user_role = UserRoles.objects.create(name='Role', description='Role Description')

    def test_user_role_creation(self):
        self.assertEqual(self.user_role.name, 'Role')
        self.assertEqual(self.user_role.description, 'Role Description')