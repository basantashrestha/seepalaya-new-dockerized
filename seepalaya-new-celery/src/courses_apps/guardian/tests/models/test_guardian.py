from django.test import TestCase
from courses_apps.account.models import PortalUser
from courses_apps.learner.models import Learner
from courses_apps.guardian.models import Guardian
from datetime import date

class GuardianModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        PortalUser.objects.create(username='testguardian', email='testguardian@example.com')
        testuser = PortalUser.objects.get(username='testguardian')
        Learner.objects.create(user=testuser, date_of_birth=date(2000, 1, 1), pin='123456', total_points=100, created_by=testuser)
        testlearner = Learner.objects.get(user=testuser)
        Guardian.objects.create(user=testuser)
        testguardian = Guardian.objects.get(user=testuser)
        testguardian.children.add(testlearner)

    def test_user_label(self):
        guardian = Guardian.objects.get(user__username='testguardian')
        field_label = guardian._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_children_label(self):
        guardian = Guardian.objects.get(user__username='testguardian')
        field_label = guardian._meta.get_field('children').verbose_name
        self.assertEqual(field_label, 'children')

    def test_object_name_is_username(self):
        guardian = Guardian.objects.get(user__username='testguardian')
        expected_object_name = f'{guardian.user.username}'
        self.assertEqual(expected_object_name, str(guardian))

    def test_children_relation(self):
        guardian = Guardian.objects.get(user__username='testguardian')
        self.assertTrue(guardian.children.exists())