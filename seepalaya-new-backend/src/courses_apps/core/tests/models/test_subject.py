from django.test import TestCase
from courses_apps.core.models import Subject

class SubjectModelTests(TestCase):

    def test_subject_creation(self):
        subject = Subject.objects.create(
            subject="Mathematics"
        )

        self.assertEqual(subject.subject, "Mathematics")

    def test_string_representation(self):
        subject = Subject.objects.create(
            subject="Mathematics"
        )
        self.assertEqual(str(subject), "Mathematics")

    def test_verbose_name(self):
        self.assertEqual(Subject._meta.verbose_name, "Subject")
        self.assertEqual(Subject._meta.verbose_name_plural, "Subject")


