import datetime
from datetime import timedelta
from django.utils import timezone
from typing import Union, List
from django.db.models import F, QuerySet
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.auth import get_user_model
from .models import UserRoles
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import PortalUser, ProfilePicture, EmailConfirmationToken
from courses_apps.learner.models import Learner
from courses_apps.teacher.models import Teacher
from courses_apps.guardian.models import Guardian

User = get_user_model()

def get_username_from_user(*, user: User) -> str:
    """
    Returns a username from the given user object.
    """
    try:
        username = user.username
    except User.DoesNotExist:
        return None
    return username

def user_get_from_username(*, username: str) -> User:
    """
    Returns a user model object that matches the given username. 
    Returns none if the user object does not exist.
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    return user

def user_get_from_email(*, email: str) -> User:
    """
    Returns a user model object that matches the given email. 
    Returns none if the user object does not exist.
    """
    try:
        user = PortalUser.objects.get(email=email)
    except User.DoesNotExist:
        return None
    return user


def check_if_email_is_taken(*, email: str) -> bool:
    """
    Returns True if the email is already taken, else False.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False


def user_email_get_from_user(*, user:User) -> str:
    """
    Returns an email associated with the given user object
    """
    try:
        email = user.email
    except PortalUser.DoesNotExist:
        return None
    return email

def email_confirmation_token_get_from_user(*, user: User) -> EmailConfirmationToken:
    """
    Returns an Email Confirmation Token object from an user object.
    """
    try:
        token = EmailConfirmationToken.objects.filter(user=user)
    except EmailConfirmationToken.DoesNotExist:
        return None
    return token
    

def token_get_from_user_and_incoming_token(*, user: str, incoming_token: str) -> QuerySet[EmailConfirmationToken]:
    """
    Returns an otp object from a given otp number. Returns None if not found.
    """
    qs = EmailConfirmationToken.objects.filter(user=user, token=incoming_token).order_by('created_time')
    if qs.exists():
        return qs.first()
    return None

def get_user_role_by_name(*, user_type: str) -> UserRoles:
    """
    Returns a user role object from the given user type.
    If the role doesn't exist, a new instance of UserRoles is returned.
    """
    try:
        user_role = UserRoles.objects.get(name=user_type)
    except UserRoles.DoesNotExist:
        user_role = UserRoles(name=user_type, description="")
        user_role.save()
    return user_role

def get_user_roles_by_user(*, user: User) -> List[UserRoles]:
    """
    Returns a queryset of user roles from the given user object.
    """
    try:
        user_types: QuerySet[UserRoles] = user.roles.all()
        return list(user_types)
    except User.DoesNotExist:
        return None


# def email_get_from_email_table_by_user(*, user: User, email: str) -> EmailAddress:
#     """
#     Returns an email address object from the given user object.
#     """
#     try:
#         email_address = EmailAddress.objects.get(user=user, email=email)
#     except EmailAddress.DoesNotExist:
#         return None
#     return email_address


# def user_get_from_email_table_by_email(*, email: str) -> User:
#     """
#     Returns a user object from the given email.
#     """
#     try:
#         email_address = EmailAddress.objects.get(email=email)
#     except EmailAddress.DoesNotExist:
#         return None
#     return email_address.user

# def check_email_verification_status(*, email: str) -> bool:
#     """
#     Returns True if the email is verified, else False.
#     """
#     try:
#         email_address = EmailAddress.objects.get(email=email)
#     except EmailAddress.DoesNotExist:
#         return False
#     return email_address.verified

# def check_if_email_exists(*, email: str) -> bool:
#     """
#     Returns True if the email exists, else False.
#     """
#     try:
#         email_address = EmailAddress.objects.get(email=email)
#     except EmailAddress.DoesNotExist:
#         return False
#     return True

# def check_email_belongs_to_user(*, email: str, user: User) -> bool:
#     """
#     Returns True if the email belongs to the user, else False.
#     """
#     try:
#         email_address = EmailAddress.objects.get(email=email, user=user)
#     except EmailAddress.DoesNotExist:
#         return False
#     return True


# def check_email_is_primary(*, email: str, user: User) -> bool:
#     """
#     Returns True if the email is primary, else False.
#     """
#     try:
#         email_address = EmailAddress.objects.get(email=email, user=user)
#     except EmailAddress.DoesNotExist:
#         return False
#     return email_address.primary

# def guardian_get_from_email(*, email: str) -> Guardian:
#     """
#     Returns a guardian object from the given email.
#     """
#     try:
#         guardian = Guardian.objects.get(user__email=email)
#     except Guardian.DoesNotExist:
#         return None
#     return guardian

def get_guardian_email_from_user(*, user: User) -> str:
    """
    Returns an email from the given user object.
    """
    try:
        guardian = Guardian.objects.get(user=user)
    except Guardian.DoesNotExist:
        return None
    return guardian.email

# def guardian_child_list(*, user: PortalUser) -> QuerySet:
#     """
#     Returns a list of child for a given guardian email.
#     """
#     try:
#         guardian = Guardian.objects.get(user=user)
#     except Guardian.DoesNotExist:
#         raise ValidationError(_("Guardian does not exist."))

#     queryset = (
#         guardian.children.prefetch_related("user") \
#         .annotate(
#             full_name=F("user__full_name"),
#             username=F("user__username"),
#         ) \
#         .values("full_name", "username")
#     )

#     return queryset



def get_user_details(*, user: User):
    """
    Returns a user object for a user.
    """
    try:
        user_roles = UserRoles.objects.filter(users_roles=user).first()
        user_type = user_roles.name if user_roles else None

        details = User.objects.annotate(
            profile=F('profile_picture__link')
        ).values("full_name", "email", "username", "profile", "is_verified").get(id=user.id)

        details['user_type'] = user_type

        if user_type == 'learner':
            learner_details = Learner.objects.filter(user=user).first()
            if learner_details:
                details['account_created_by'] = learner_details.account_created_by
    except User.DoesNotExist:
        return None
    return details

def all_profile_pictures_get(user: User) -> QuerySet[ProfilePicture]:
    pictures = ProfilePicture.objects.all()
    return pictures

def profile_picture_get_from_uid(*, uid) -> ProfilePicture:
    try:
        picture = ProfilePicture.objects.get(uid=uid)
    except ProfilePicture.DoesNotExist:
        return None
    return picture

def check_verification_requirement(user: User) -> bool:
    """
    Returns True if the user needs to be verified, else False.
    The verification requirement is based on the account creation date.
    Also, the account should be maintained by the learner.
    i.e. if the account had been created by a teacher they have a dummy email and can't verify.
    """
    try:
        if hasattr(user, 'teacher'):
            return False
        if hasattr(user, 'learner'):
            if user.learner.account_maintained_by != 'LEARNER':
                return False
            is_verified = user.is_verified
            if is_verified:
                return False
            else:
                created_date = user.date_joined
                if created_date + timedelta(days=15) < timezone.now():
                    return True
    except User.DoesNotExist:
        return False
    return False
