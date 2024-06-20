from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from dataclasses import dataclass
from typing import List, Dict
from .helpers import generate_usernames_emails_and_passwords
from courses_apps.classroom.models import ClassRoom
from courses_apps.teacher.models import Teacher
from courses_apps.learner.models import Learner
from courses_apps.account.services import user_signup, batch_create_users
from courses_apps.account.selectors import user_get_from_username
from courses_apps.teacher.selectors import teacher_get_from_username
from .selectors import get_classroom_from_code
from .helpers import generate_class_code

from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
import logging
from gettext import gettext as _
from django.contrib.auth import get_user_model

User = get_user_model()

# Set up logging
logger = logging.getLogger(__name__)

@transaction.atomic
def create_classroom(*, title: str, teacher: Teacher) -> ClassRoom:
    """
    Creates a class with the provided name and teacher.
    """
    try:
        class_code = generate_class_code()
        classroom = ClassRoom(title=title, teacher=teacher, class_code=class_code)
        classroom.full_clean()
        classroom.save()
        return classroom
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])


@transaction.atomic
def update_classroom(*, class_code: str, title: str, teacher_user: str) -> dict:
    """
    Updates the title of a classroom with the provided class code.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise ValidationError(_("Classroom does not exist."))
    teacher = teacher_get_from_username(username=teacher_user)
    if not classroom.teacher == teacher:
        raise ValidationError(_("Teacher is not the owner of the classroom."))
    try:
        classroom.title = title
        classroom.full_clean()
        classroom.save(update_fields=["title"])
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])

    return {"title": title}

@transaction.atomic
def delete_classroom(*, class_code: str, teacher_user: str) -> bool:
    """
    Deletes a classroom with the provided class code.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise ValidationError(_("Classroom does not exist."))
    teacher = teacher_get_from_username(username=teacher_user)
    if not classroom.teacher == teacher:
        raise ValidationError(_("Teacher is not the owner of the classroom."))
    classroom.delete()
    return True


@transaction.atomic
def student_create(class_code: str, students: List[str], teacher_user: str) -> List[Dict[str, str]]:
    """
    Signs up students and returns a list of StudentSignupDetails dictionaries.
    """
    @dataclass
    class StudentSignupDetails:
        full_name: str
        username: str
        email: str
        password: str

    user_type = "learner"
    created_students = []
    created_users = []

    # Generate usernames, emails, and passwords
    student_details = generate_usernames_emails_and_passwords(students)

    # Collect user details for batch creation
    for details in student_details:
        created_users.append({
            'username': details['username'],
            'full_name': details['full_name'],
            'email': details['email'],
            'password': details['password'],
            'user_type': user_type,
            # 'bypass_flag': True  # Assuming we bypass validation for simplicity
        })

    # Batch create users asynchronously
    created_users_objects = batch_create_users(created_users)

    # Create students and associate with classroom and teacher
    for user_obj, details in zip(created_users_objects, student_details):
        user = user_obj

        student = Learner(user=user, account_maintained_by="TEACHER")
        student.full_clean()
        student.save()

        classroom = get_classroom_from_code(class_code=class_code)
        if classroom is None:
            raise ValidationError(_("Classroom does not exist."))
        classroom.students.add(user)
        classroom.save()

        teacher = teacher_get_from_username(username=teacher_user)
        if teacher is None:
            raise ValidationError(detail=_("Teacher does not exist."))
        teacher.students.add(user)
        teacher.save()

        created_students.append(StudentSignupDetails(
            full_name=details['full_name'],
            username=details['username'],
            email=details['email'],
            password=details['password']
        ))

    return created_students

@transaction.atomic
def join_classroom(*, class_code: str, username: str):
    """
    Adds a student to a classroom with the provided class code and username.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise ValidationError(_("Classroom does not exist."))
    student = user_get_from_username(username=username)
    check_user = classroom.students.filter(username=username)
    if check_user.exists():
        raise ValidationError(_("Student is already in the classroom."))
    classroom.students.add(student)
    classroom.save()
    return classroom.title


@transaction.atomic
def add_students_to_classroom(*, class_code: str, students: list, teacher_user: str) -> bool:
    """
    Adds students to a classroom with the provided class code.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise ValidationError(_("Classroom does not exist."))
    teacher = teacher_get_from_username(username=teacher_user)
    if not classroom.teacher == teacher:
        raise ValidationError(_("Teacher is not the owner of the classroom."))
    for student in students:
        student = user_get_from_username(username=student)
        check_teacher_student_relation = teacher.students.filter(username=student)
        if not check_teacher_student_relation.exists():
            raise ValidationError(_("The user is not a student of the teacher."))
        # no need to check if student is already in the classroom causes failure of the bulk add
        # check_user = classroom.students.filter(username=student)
        # if check_user.exists():
        #     raise ValidationError(_("Student is already in the classroom."))
        classroom.students.add(student)
        teacher.students.add(student)
    classroom.save()
    teacher.save()
    return True

@transaction.atomic
def remove_students_from_classroom(*, class_code: str, students: list, teacher_user: str) -> bool:
    """
    Removes students from a classroom with the provided class code.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise ValidationError(_("Classroom does not exist."))
    teacher = teacher_get_from_username(username=teacher_user)
    if not classroom.teacher == teacher:
        raise ValidationError(_("Teacher is not the owner of the classroom."))
    for student in students:
        student = user_get_from_username(username=student)
        check_teacher_student_relation = teacher.students.filter(username=student)
        if not check_teacher_student_relation.exists():
            raise ValidationError(_("The user is not a student of the teacher."))
        # check_user = classroom.students.filter(username=student)
        # if not check_user.exists():
        #     raise ValidationError(_("Student is not in the classroom."))
        classroom.students.remove(student)
    classroom.save()
    return True
