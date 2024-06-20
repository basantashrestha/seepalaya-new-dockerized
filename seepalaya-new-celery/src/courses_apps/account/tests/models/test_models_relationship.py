from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model
from courses_apps.account.models import ProfilePicture, UserRoles, PortalUser, EmailConfirmationToken
from courses_apps.guardian.models import Guardian
from courses_apps.learner.models import Learner
from courses_apps.teacher.models import Teacher

User = get_user_model()
class TestModelRelationships(TestCase):

    def setUp(self):
        self.user = mixer.blend(User)
        self.portal_user = mixer.blend(PortalUser, username='testuser', full_name='Test User')
        self.profile_picture = mixer.blend(ProfilePicture, name='testpic', link='http://test.com/pic.jpg')
        self.user_role = mixer.blend(UserRoles, name='testrole', description='Test Role')
        self.learner = mixer.blend(Learner, user=self.portal_user, date_of_birth='2000-01-01', pin='123456', total_points=100)
        self.teacher = mixer.blend(Teacher, user=self.portal_user, school='Test School')
        self.guardian = mixer.blend(Guardian, user=self.portal_user)
        self.email_confirmation_token = mixer.blend(EmailConfirmationToken, user=self.portal_user, token='testtoken')

        # Assign profile picture and role to portal user
        self.portal_user.profile_picture = self.profile_picture
        self.portal_user.roles.add(self.user_role)
        self.portal_user.save()

        # Assign learner to guardian
        self.guardian.children.add(self.learner)
        self.guardian.save()

    def test_portal_user_profile_picture(self):
        self.assertEqual(self.portal_user.profile_picture, self.profile_picture)

    def test_portal_user_roles(self):
        self.assertIn(self.user_role, self.portal_user.roles.all())

    def test_learner_user(self):
        self.assertEqual(self.learner.user, self.portal_user)

    def test_teacher_user(self):
        self.assertEqual(self.teacher.user, self.portal_user)

    def test_guardian_user(self):
        self.assertEqual(self.guardian.user, self.portal_user)

    def test_guardian_children(self):
        self.assertIn(self.learner, self.guardian.children.all())

    def test_email_confirmation_token_user(self):
        self.assertEqual(self.email_confirmation_token.user, self.portal_user)