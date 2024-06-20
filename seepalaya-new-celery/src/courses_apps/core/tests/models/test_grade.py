from django.test import TestCase
from courses_apps.core.models import Grade

class GradeModelTests(TestCase):

    def test_grade_creation(self):
        grade = Grade.objects.create(
            grade="Grade 1",
            in_symbol="G1"
        )

        self.assertEqual(grade.grade, "Grade 1")
        self.assertEqual(grade.in_symbol, "G1")

    def test_string_representation(self):
        grade = Grade.objects.create(
            grade="Grade 1",
            in_symbol="G1"
        )
        self.assertEqual(str(grade), "Grade 1 (G1)")

    def test_verbose_name(self):
        self.assertEqual(Grade._meta.verbose_name, "Grade")
        self.assertEqual(Grade._meta.verbose_name_plural, "Grade")