from django.test import TestCase
from courses_apps.teacher.models import Teacher
from courses_apps.account.models import PortalUser
from django.contrib.auth import get_user_model

User = get_user_model()

class TeacherModelTests(TestCase):

    def setUp(self):

        self.teacher_user = PortalUser.objects.create_user(
            username="teacher1",
            email="teacher1@example.com",
            password="password",
            full_name="Teacher One",
        )

        self.student1 = PortalUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="password",
            full_name="Student One"
        )

        self.student2 = PortalUser.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="password",
            full_name="Student Two"
        )

    def test_teacher_creation(self):
        teacher = Teacher.objects.create(
            user=self.teacher_user,
            school="Example School"
        )
        teacher.students.add(self.student1, self.student2)

        self.assertEqual(teacher.user, self.teacher_user)
        self.assertEqual(teacher.school, "Example School")
        self.assertIn(self.student1, teacher.students.all())
        self.assertIn(self.student2, teacher.students.all())

    def test_string_representation(self):
        teacher = Teacher.objects.create(
            user=self.teacher_user,
            school="Example School"
        )
        self.assertEqual(str(teacher), "teacher1")

    def test_verbose_name(self):
        self.assertEqual(Teacher._meta.verbose_name, "Teacher")
        self.assertEqual(Teacher._meta.verbose_name_plural, "Teachers")

    def test_many_to_many_students(self):
        teacher = Teacher.objects.create(
            user=self.teacher_user,
            school="Example School"
        )
        teacher.students.add(self.student1, self.student2)
        self.assertEqual(teacher.students.count(), 2)
        self.assertIn(self.student1, teacher.students.all())
        self.assertIn(self.student2, teacher.students.all())
