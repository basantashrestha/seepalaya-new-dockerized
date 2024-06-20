from .models import Guardian
from courses_apps.account.models import PortalUser
from courses_apps.learner.models import Learner
from django.db.models import QuerySet
from django.db.models import F
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.postgres.aggregates import ArrayAgg


User = get_user_model()

def guardian_get_from_email(*, email: str) -> Guardian:
    """
    Returns a guardian object from the given email.
    """
    try:
        guardian = Guardian.objects.get(user__email=email)
    except Guardian.DoesNotExist:
        return None
    return guardian

def guardian_get_all_children(*, guardian: Guardian) -> QuerySet[Learner]:
    """
    Used only for validation/internal purposes.
    Returns a list of all children associated with a given guardian object.
    Returns none if no children are available.
    """
    children = guardian.children.all()
    if children is None:
        return None
    return children

def child_get_from_username(*, username: str) -> Learner:
    """
    Returns a child object from the given username.
    """
    try:
        child = Learner.objects.get(user__username=username)
    except Learner.DoesNotExist:
        return None
    return child

def child_get_from_email(*, email:str) -> Learner:
    """
    Returns a child object from the given email address.
    """
    try:
        child = Learner.objects.get(user__email=email)
    except Learner.DoesNotExist:
        return None
    return child

def check_learner_account_created_by(*, learner: Learner) -> str:
    """
    Returns the account created by field for a given learner object.
    """
    return learner.account_created_by

def check_child_belongs_to_guardian(*, guardian: Guardian, child: Learner) -> bool:
    """
    Checks if a child belongs to a guardian.
    """
    if child in guardian.children.all():
        return True
    return False

def get_user_detail_for_child(*, user: PortalUser):
    """
    Returns a user object for a child user.
    """
    try:
        details = User.objects.annotate(
            # user_email=F("child__guardian__email"), 
            profile=F('profile_picture__link'))\
                .values("full_name", "username", "profile", "is_verified").get(id=user.id)
    except User.DoesNotExist:
        return None
    return details

def user_email_get_from_user(*, user:User) -> str:
    """
    Returns an email associated with the given user object
    """
    try:
        email = user.email
    except PortalUser.DoesNotExist:
        return None
    return email

def guardian_get_from_user(*, user: User) -> Guardian:
    """
    Returns a guardian object from the given user object.
    """
    try:
        guardian = Guardian.objects.get(user=user)
    except Guardian.DoesNotExist:
        return None
    return guardian

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

def guardian_child_list(*, user: PortalUser) -> QuerySet:
    """
    Returns a list of child for a given guardian email.
    """
    try:
        guardian = Guardian.objects.get(user=user)
    except Guardian.DoesNotExist:
        raise ValidationError(_("Guardian does not exist."))

    queryset = (
        guardian.children.prefetch_related("user") \
        .annotate(
            full_name=F("user__full_name"),
            username=F("user__username"),
            # user_type=F("user__roles__name"),
            user_type=ArrayAgg("user__roles__name", distinct=True),
            account_creator = F("account_created_by")

        ) \
        .values("full_name", "username", "user_type", "account_creator")
    )

    return queryset