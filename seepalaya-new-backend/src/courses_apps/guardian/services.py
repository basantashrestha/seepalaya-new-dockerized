from dataclasses import dataclass
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from courses_apps.account.services import user_signup
from .models import Guardian
from courses_apps.account.helpers import construct_username_from_email
from django.contrib.auth import get_user_model
from courses_apps.guardian.selectors import (
    guardian_get_from_email, guardian_get_all_children, child_get_from_username, 
    check_learner_account_created_by, check_child_belongs_to_guardian, get_user_detail_for_child, 
    user_email_get_from_user, guardian_get_from_user, user_get_from_username, child_get_from_email
)
from .helpers import construct_email_for_child
from courses_apps.learner.models import Learner
from datetime import date


User = get_user_model()

@transaction.atomic
def guardian_signup(
    *,
    # full_name: str, 
    # username: str, 
    email: str, 
    password: str, 
    confirm_password: str
) -> object:
    """
    Signs up and returns a GuardianSignupDetails dataclass object.
    Sends email confirmation after the signup is complete.
    """
    @dataclass(frozen=True)
    class GuardianSignupDetails:
        user_type: str
        username: str
        # full_name: str
        email: str
        is_verified: bool
        access_token: str

    user_type = "guardian"
    username = construct_username_from_email(email=email)
    try:
        user = user_signup(
            # full_name=full_name,
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            user_type=user_type,
        )
    except ValidationError as e:
        raise ValidationError(detail=_(e.detail[0]))
    
    try:
        guardian = Guardian(user=user)
        guardian.full_clean()
    except DjangoValidationError as e:
        raise ValidationError(detail=_(str(e.message)))
    
    guardian.save()

    token = RefreshToken.for_user(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    is_verified = user.is_verified
    user_type = user_type

    signup_details = GuardianSignupDetails(
        user_type, username, email, is_verified, access_token
    )

    return signup_details, refresh_token



@transaction.atomic
def child_signup(*, guardian_user: User, full_name:str, username: str, pin: str, confirm_pin: str, date_of_birth: date ) -> object:
    """
    Signs up a child and returns a ChildSignupDetails dataclass object.
    """

    @dataclass
    class ChildSignupDetails:
        user_type: str
        username: str
        full_name: str
        guardian_email: str
        user_email: str
        is_verified: bool

    user_type = "learner"
    guardian_email = user_email_get_from_user(user=guardian_user) 
    username = username.lower()
    user_email = construct_email_for_child(username=username, email=guardian_email)
    print(pin)
    try:
        user = user_signup(
            username=username,
            full_name=full_name,
            email=user_email,
            password=pin,
            confirm_password=pin,
            user_type=user_type,
            bypass_flag = True
        )
        print(f"Full user object: {user}")
    except ValidationError as e:
        raise ValidationError(detail=_(e.detail[0]))
    if len(pin) < 6:
        raise ValidationError(detail=_("Pin must be at least 6 characters long."))
    
    child = Learner(user=user, date_of_birth=date_of_birth, created_by=guardian_user, account_created_by="GUARDIAN")
    child.full_clean()
    child.save()

    guardian = guardian_get_from_email(email=guardian_email.lower())
    if guardian is None:
        raise ValidationError(detail=_("Guardian does not exist."))
    
    guardian.children.add(child)
    guardian.save()
    
    # print(f"is_verified from user: {user.is_verified}")  # Print the value

    guardian_email = guardian_email
    is_verified = user.is_verified
    user_type = user_type

    child_signup_details = ChildSignupDetails(
        user_type, username, full_name, guardian_email, user_email, is_verified
    )

    return child_signup_details

@transaction.atomic
def child_update(*, user: User, child_username: str, **kwargs) -> Learner:
    """
    Updates the child user.
    """
    guardian = guardian_get_from_user(user=user)
    child = child_get_from_username(username=child_username)
    child_user = child.user
#    child_modify = check_guardian_can_modify_child(user=child_user)
    child_account_creator = check_learner_account_created_by(learner=child)
    pin = kwargs.get("pin", None)
    kwargs_keys = kwargs.keys()


    if not child in guardian_get_all_children(guardian=guardian):
        raise ValidationError(detail=_("Child does not belong to the guardian."))
    if child is None:
        raise ValidationError(detail=_("Child does not exist."))
    if child_account_creator == 'LEARNER':
        raise ValidationError(detail=_("Guardian cannot modify this child."))
    if pin is not None:
        if len(pin) < 6:
            raise ValidationError(detail=_("Pin must be at least 6 characters long."))
        if not str(pin).isdigit():
            raise ValidationError(detail=_("Pin must be a number."))
        # child.pin = pin
        # child.save(update_fields=["pin"])
        child_user.set_password(pin)
        child_user.save(update_fields=["password"])

    if 'full_name' in kwargs_keys:
        full_name = kwargs.pop("full_name")
        child_user.full_name = full_name
        child.user.save(update_fields=["full_name"])

    if 'username' in kwargs:
        username = kwargs.pop("username")
        if len(username) < 6:
            raise ValidationError(detail=_("Username must be at least 6 characters long."))
        child_user.username = username
        child_user.save(update_fields=["username"])

    user_details = get_user_detail_for_child(user=child_user)
    return user_details

@transaction.atomic
def guardian_remove_child(*, guardian: Guardian, child: Learner) -> None:
    """
    Removes a child from a guardian's list of children.
    """
    try:
        guardian.children.remove(child)
    except Exception as e:
        return None
    return True


@transaction.atomic
def child_delete(*, user: User, child_username: str) -> bool:
    """
    Deletes the child user.
    """
    child = child_get_from_username(username=child_username)
    child_user = user_get_from_username(username=child_username)
    guardian = guardian_get_from_user(user=user)
#    child_modify = check_guardian_can_modify_child(user=child_user)
    child_account_creator = check_learner_account_created_by(learner=child)
    if child is None:
        raise ValidationError(detail=_("Child does not exist."))
    if guardian is None:
        raise ValidationError(detail=_("Guardian does not exist."))
    if child_account_creator == 'LEARNER':
        raise ValidationError(detail=_("Guardian cannot modify this child."))

    child_belongs_to_guardian = check_child_belongs_to_guardian(guardian=guardian, child=child)
    if not child_belongs_to_guardian:
        raise ValidationError(detail=_("Guardian not associated with child."))
    is_removed = guardian_remove_child(guardian=guardian, child=child)
    child.user.delete()
    child.delete()
    return is_removed


    

