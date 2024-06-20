from typing import List, Dict, Any, Union
from django.db.models.query import QuerySet
from django.db.models import F
from django.contrib.auth import get_user_model
from courses_apps.teacher.models import Teacher
from courses_apps.account.models import PortalUser
from courses_apps.learner.models import Learner
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.postgres.aggregates import ArrayAgg
from courses_apps.classroom.models import ClassRoom
from django.db.models import Count
from django.core.exceptions import ValidationError as DjangoValidationError


User = get_user_model()

def teacher_get_from_email(*, email: str) -> Teacher:
    """
    Returns a teacher object from the given email.
    """
    try:
        teacher = Teacher.objects.get(user__email=email)
    except Teacher.DoesNotExist:
        return None
    return teacher

def teacher_get_from_user(*, user: User) -> Teacher:
    """
    Returns a teacher object from the given user object.
    """
    try:
        teacher = Teacher.objects.get(user=user)
    except Teacher.DoesNotExist:
        return None
    return teacher

def teacher_get_from_username(*, username: str) -> Teacher:
    """
    Returns a teacher object from the given username.
    """
    try:
        teacher = Teacher.objects.get(user__username=username)
    except Teacher.DoesNotExist:
        return None
    return teacher


def teacher_get_all_students(*, teacher: Teacher) -> QuerySet[Learner]:
    """
    Used only for validation/internal purposes.
    Returns a list of all students associated with a given teacher object.
    Returns none if no students are available.
    """
    students = teacher.students.all()
    if students is None:
        return None
    return students

def student_get_from_username(*, username: str) -> Learner:
    """
    Returns a child object from the given username.
    """
    try:
        student = Learner.objects.get(user__username=username)
    except Learner.DoesNotExist:
        return None
    return student

def check_learner_account_created_by(*, learner: Learner) -> str:
    """
    Returns the account created by field for a given learner object.
    """
    return learner.account_created_by


def get_user_detail_for_student(*, user: PortalUser):
    """
    Returns a user object for a student user.
    """
    try:
        details = User.objects.annotate(
            # user_email=F("child__guardian__email"), 
            profile=F('profile_picture__link'))\
                .values("full_name", "username", "profile", "is_verified").get(id=user.id)
    except User.DoesNotExist:
        return None
    return details

def teacher_student_list(*, user: PortalUser) -> QuerySet:
    """
    Returns a list of students for a given teacher email, including the created_by field.
    """
    try:
        teacher = Teacher.objects.get(user=user)
    except Teacher.DoesNotExist:
        raise ValidationError(_("Teacher does not exist."))

    queryset = (
        teacher.students.prefetch_related("learner", "classes")
        .annotate(
            student_full_name=F("full_name"),
            student_username=F("username"),
            student_maintained_by=F("learner__account_maintained_by"),
            classroom=F("classes__title"),
        )
        .values("student_full_name", "student_username", "student_maintained_by", "classroom")
    )

    return queryset



def get_teacher_classroom_list(*, exclude: str, teacher_user: User) -> list:
    """
    Returns a list of classrooms associated with a given teacher, excluding
    the classroom with the specified class_code.
    """
    teacher = teacher_get_from_user(user=teacher_user)
    if not teacher:
        raise DjangoValidationError(_("Teacher does not exist."))

    queryset = (
        ClassRoom.objects.filter(teacher=teacher)
        .exclude(class_code=exclude)
        .prefetch_related("students")
        .annotate(
            classroom_title=F("title"),
            classroom_code=F("class_code"),
            student_count=Count("students"),
        )
        .values("classroom_title", "classroom_code", "student_count")
        .order_by("-student_count")
    )
    
    return list(queryset)