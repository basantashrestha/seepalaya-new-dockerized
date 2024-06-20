from django.test import TestCase
from courses_apps.learner.models import Learner
from courses_apps.account.models import PortalUser

class LearnerModelTests(TestCase):

    def setUp(self):
        self.user = PortalUser.objects.create_user(
            username="learner1",
            email="learner1@example.com",
            password="password",
            full_name="Learner One",
        )

    def test_learner_creation(self):
        learner = Learner.objects.create(
            user=self.user,
            date_of_birth="2000-01-01",
            pin="123456",
            total_points=100,
            account_maintained_by="GUARDIAN"
        )

        self.assertEqual(learner.user, self.user)
        self.assertEqual(learner.date_of_birth, "2000-01-01")
        self.assertEqual(learner.pin, "123456")
        self.assertEqual(learner.total_points, 100)
        self.assertEqual(learner.account_maintained_by, "GUARDIAN")

    def test_string_representation(self):
        learner = Learner.objects.create(
            user=self.user,
            date_of_birth="2000-01-01",
            pin="123456",
            total_points=100,
            account_maintained_by="GUARDIAN"
        )
        self.assertEqual(str(learner), "learner1")

    def test_default_account_maintained_by(self):
        learner = Learner.objects.create(
            user=self.user
        )
        self.assertEqual(learner.account_maintained_by, "LEARNER")

    def test_verbose_name(self):
        self.assertEqual(Learner._meta.verbose_name, "Learner")
        self.assertEqual(Learner._meta.verbose_name_plural, "Learners")

