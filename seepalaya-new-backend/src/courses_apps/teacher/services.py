from dataclasses import dataclass
from typing import List
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from courses_apps.account.services import user_signup
from .models import Teacher
from courses_apps.account.helpers import construct_username_from_email
from django.contrib.auth import get_user_model
from courses_apps.teacher.selectors import (
    teacher_get_from_email, teacher_get_from_user, teacher_get_all_students, student_get_from_username, check_learner_account_created_by, 
    get_user_detail_for_student
)
from courses_apps.learner.models import Learner
from courses_apps.account.selectors import user_get_from_username, user_email_get_from_user, get_user_roles_by_user, check_verification_requirement
from .helpers import construct_email_for_child

User = get_user_model()

@transaction.atomic
def teacher_signup(
    *,
    full_name: str, 
    # username: str, 
    email: str, 
    password: str, 
    confirm_password: str
) -> object:
    """
    Signs up and returns a TeacherSignupDetails dataclass object.
    Sends email confirmation after the signup is complete.
    """
    @dataclass(frozen=True)
    class TeacherSignupDetails:
        user_type: List[str]
        username: str
        full_name: str
        user_email: str
        is_verified: bool
        access_token: str
        staff: bool
        superuser: bool
        verification_required: bool

    user_type = "teacher"
    username = construct_username_from_email(email=email)
    try:
        user = user_signup(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            user_type=user_type,
        )
    except ValidationError as e:
        raise ValidationError(detail=_(e.detail[0]))
    
    try:
        teacher = Teacher(user=user)
        teacher.full_clean()
    except DjangoValidationError as e:
        raise ValidationError(detail=_(str(e)))
    
    teacher.save()

    token = RefreshToken.for_user(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    is_verified = user.is_verified
    staff = False
    superuser = False
    user_type = get_user_roles_by_user(user=user)
    verification_required = check_verification_requirement(user=user)
    user_email=email

    signup_details = TeacherSignupDetails(
        user_type, username, full_name,user_email, is_verified, access_token, staff, superuser, verification_required
    )

    return signup_details, refresh_token



@transaction.atomic
def student_signup(*, teacher_user: User, full_name: str, username: str, password: str) -> object:
    """
    Signs up a student and returns a StudentSignupDetails dataclass object.
    """
    
    @dataclass
    class StudentSignupDetails:
        user_type: str
        username: str
        full_name: str
        teacher_user: str
        user_email: str
        is_verified: bool
    user_type = "learner"
    teacher_email = user_email_get_from_user(user=teacher_user) 
    username = username.lower()
    user_email = construct_email_for_child(username=username, email=teacher_email)
    try:
        user = user_signup(
            username=username,
            full_name=full_name,
            email=user_email,
            password=password,
            confirm_password=password,
            user_type=user_type,
            bypass_flag=True
        )
        print(f"Full student user object: {user}")
    except ValidationError as e:
        raise ValidationError(detail=_(e.detail[0]))
    if len(password) < 8:
        raise ValidationError(detail=_("Password must be at least 8 characters long."))
    
    student = Learner(user=user, created_by=teacher_user, account_created_by="TEACHER")
    student.full_clean()
    student.save()

    teacher = teacher_get_from_email(email=teacher_email.lower())
    if teacher is None:
        raise ValidationError(detail=_("Teacher does not exist."))
    
    teacher.students.add(student)
    teacher.save()
    
    print(f"is_verified from user: {user.is_verified}")

    teacher_email = teacher_email
    is_verified = user.is_verified
    user_type = user_type

    student_signup_details = StudentSignupDetails(
        user_type, username, full_name, teacher_email, user_email, is_verified
    )

    return student_signup_details


@transaction.atomic
def student_update(*, user: User, student_username: str, **kwargs) -> Learner:
    """
    Updates the child user.
    """
    teacher = teacher_get_from_user(user=user)
    student = student_get_from_username(username=student_username)
    student_user = student.user
    student_account_creator = check_learner_account_created_by(learner=student)
    password = kwargs.get("password", None)
    kwargs_keys = kwargs.keys()


    if not student in teacher_get_all_students(teacher=teacher):
        raise ValidationError(detail=_("student does not belong to the teacher."))
    if student is None:
        raise ValidationError(detail=_("student does not exist."))
    if student_account_creator == 'LEARNER':
        raise ValidationError(detail=_("Teacher cannot modify this student."))
    if password is not None:
        if len(password) < 6:
            raise ValidationError(detail=_("Pin must be at least 6 characters long."))
        student_user.set_password(password)
        student_user.save(update_fields=["password"])

    if 'full_name' in kwargs_keys:
        full_name = kwargs.pop("full_name")
        student_user.full_name = full_name
        student.user.save(update_fields=["full_name"])

    if 'username' in kwargs:
        username = kwargs.pop("username")
        if len(username) < 8:
            raise ValidationError(detail=_("Username must be at least 8 characters long."))
        student_user.username = username
        student_user.save(update_fields=["username"])

    user_details = get_user_detail_for_student(user=student_user)
    return user_details

@transaction.atomic
def teacher_remove_student(*, teacher: Teacher, student: Learner) -> bool:
    """
    Removes a student from a teacher's list of students.
    """
    try:
        teacher.students.remove(student)
    except Exception as e:
        return None
    return True

@transaction.atomic
def student_delete(*, user: User, student_username: str) -> bool:
    """
    Deletes the student user.
    """
    student = student_get_from_username(username=student_username)
    student_user = user_get_from_username(username=student_username)
    teacher = teacher_get_from_user(user=user)
    student_account_creator = check_learner_account_created_by(learner=student)
    if student is None:
        raise ValidationError(detail=_("student does not exist."))
    if teacher is None:
        raise ValidationError(detail=_("teacher does not exist."))
    if not student in teacher_get_all_students(teacher=teacher):
        raise ValidationError(detail=_("student does not belong to the teacher."))
    if student_account_creator == 'LEARNER':
        raise ValidationError(detail=_("teacher cannot modify this student."))

    is_removed = teacher_remove_student(teacher=teacher, student=student)
    student.user.delete()
    student.delete()
    return is_removed

