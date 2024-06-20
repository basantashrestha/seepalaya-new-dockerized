from django.test import TestCase
from django.core.exceptions import ValidationError
from courses_apps.classroom.models import ClassRoom
from courses_apps.teacher.models import Teacher
from courses_apps.account.models import PortalUser, ProfilePicture
from django.contrib.auth import get_user_model

User = get_user_model()

class ClassRoomModelTests(TestCase):

    def setUp(self):

        # Create PortalUser for teacher
        self.teacher_user = PortalUser.objects.create_user(
            username="teacher1",
            email="teacher1@example.com",
            password="password",
            full_name="John Doe",
        )

        # Create Teacher instance
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            school="Example School"
        )

        # Create PortalUser instances for students
        self.student1 = PortalUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="password",
            full_name="Jane Smith"
        )

        self.student2 = PortalUser.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="password",
            full_name="John Smith"
        )

    def test_classroom_creation(self):
        classroom = ClassRoom.objects.create(
            title="Math 101",
            class_code="MATH101",
            teacher=self.teacher
        )
        classroom.students.add(self.student1, self.student2)

        self.assertEqual(classroom.title, "Math 101")
        self.assertEqual(classroom.class_code, "MATH101")
        self.assertEqual(classroom.teacher, self.teacher)
        self.assertIn(self.student1, classroom.students.all())
        self.assertIn(self.student2, classroom.students.all())

    def test_title_validation(self):
        with self.assertRaises(ValidationError):
            classroom = ClassRoom(
                title="Math",  # Less than 5 characters
                class_code="MATH102",
                teacher=self.teacher
            )
            classroom.full_clean()  # This will trigger the validation

    def test_class_code_uniqueness(self):
        ClassRoom.objects.create(
            title="Math 101",
            class_code="MATH101",
            teacher=self.teacher
        )

        with self.assertRaises(ValidationError):
            classroom = ClassRoom(
                title="Physics 101",
                class_code="MATH101",  # Duplicate class code
                teacher=self.teacher
            )
            classroom.full_clean()  # This will trigger the validation

    def test_string_representation(self):
        classroom = ClassRoom.objects.create(
            title="Biology 101",
            class_code="BIO101",
            teacher=self.teacher
        )
        self.assertEqual(str(classroom), "Biology 101")

    def test_verbose_name(self):
        self.assertEqual(ClassRoom._meta.verbose_name, 'Class')
        self.assertEqual(ClassRoom._meta.verbose_name_plural, 'Classes')

    def test_many_to_many_students(self):
        classroom = ClassRoom.objects.create(
            title="History 101",
            class_code="HIST101",
            teacher=self.teacher
        )
        classroom.students.add(self.student1, self.student2)
        self.assertEqual(classroom.students.count(), 2)
        self.assertIn(self.student1, classroom.students.all())
        self.assertIn(self.student2, classroom.students.all())
