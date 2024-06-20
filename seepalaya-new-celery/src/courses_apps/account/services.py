import logging
from dataclasses import dataclass
from typing import List, Optional
from .models import (
    PortalUser, EmailConfirmationToken, UserRoles
)
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework.exceptions import APIException, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .helpers import (
    send_email_confirmation, identify_email_or_username, send_reset_password_link,
)
from .selectors import (
    user_get_from_username, user_get_from_email, token_get_from_user_and_incoming_token, user_email_get_from_user,
    email_confirmation_token_get_from_user, get_user_role_by_name, get_username_from_user, get_user_roles_by_user,
    check_if_email_is_taken,
    profile_picture_get_from_uid,
    check_verification_requirement
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from rest_framework import status

logger = logging.getLogger('django.server')

User = get_user_model()

@transaction.atomic
def user_signup(
    *,
    username: str,
    email:str,
    password: str,
    confirm_password: str,
    user_type: str,
    full_name: str,
    bypass_flag: Optional[bool] = False
) -> PortalUser:
    """
    Signs up the user and returns a user object.
    """
    if password is None and confirm_password is None:
        raise ValidationError(detail="Password field cannot be empty for learners and teachers.")
    
    if password != confirm_password:
        raise ValidationError(
            detail="Password & confirm password fields do not match."
        )

    # validate password
    if not bypass_flag:
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise ValidationError(e.messages[0])

    verification_status = False
    if bypass_flag:
        verification_status = True

    # check for existing user and raise a validation error.
    exisiting_user = check_if_email_is_taken(email=email.lower())
    if exisiting_user:
        raise ValidationError(detail=_("User with the email already exists."))
    
    existing_username = user_get_from_username(username=username.lower())
    if existing_username is not None:
        raise ValidationError(detail=f"User with the username `{username}` already exists.")

    user = User(
        full_name=full_name,
        username=username.lower(),
        email=email.lower(),
        is_verified=verification_status,
    )

    try:
        user.set_password(password)
        print("Attempting to clean the user.")
        user.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    print("Attempting to save the user.")
    user.save()

    # email_address = EmailAddress(user=user, email=email.lower(), verified=False, primary=True)
    # email_address.save()

    try:
        user_role = get_user_role_by_name(user_type=user_type)
        user.roles.add(user_role)
        user.save()
    except UserRoles.DoesNotExist:
        raise ValidationError(detail=_("User role does not exist."))
    return user


def user_login(*, username_or_email: str, password: str) -> tuple:
    """
    Verifies user's credentials & returns access token & refresh token.
    """

    @dataclass(frozen=True)
    class UserLoginDetails:
        user_type: List[str]
        username: str
        user_email: str
        full_name: str
        is_verified: bool
        access_token: str
        staff: bool
        superuser: bool
        verification_required: bool
    
    credential_type = identify_email_or_username(credential=username_or_email)
    if credential_type == "email":
        user = user_get_from_email(email=username_or_email.lower())
    else:
        user = user_get_from_username(username=username_or_email.lower())

    if user is None:
        raise ValidationError(detail=_("Invalid credentials."))

    if not user.check_password(password):
        raise ValidationError(detail=_("Invalid credentials."))

    username = user.username
    user_email = user.email
    full_name = user.full_name
    is_verified = user.is_verified
    user_type = get_user_roles_by_user(user=user)
    staff = user.is_staff
    superuser = user.is_superuser
    verification_required = check_verification_requirement(user=user)

    print(user_type)

    token = RefreshToken.for_user(user)
    access_token = str(token.access_token)
    refresh_token = str(token)

    user_login_details = UserLoginDetails(
        user_type, username, user_email, full_name, is_verified, access_token, staff, superuser, verification_required
    )

    return user_login_details, refresh_token


@transaction.atomic
def user_send_forgot_password_email(*, email: str) -> bool:
    """
    Sends a forgot password link to the user.
    """
    user = user_get_from_email(email=email.lower())
    if user is None:
        raise ValidationError(detail=_("Please enter a valid email address."))
    token = get_random_string(length=64)
    user.password = token
    user.save()

    #Sending the reset link
    link = f"http://192.168.5.22:3000/account/reset-password/{user.username}/{token}"
    email = send_reset_password_link(link=link, receiver_email=email)
    if email is True:
        return True
    raise APIException(detail=_("There was some error, email could not be sent."))


@transaction.atomic
def user_reset_password(*, username: str, token: str, password: str, confirm_password: str) -> bool:
    """
    Resets password for guardian.
    """
    user = user_get_from_username(username=username)
    if user is None:
        raise ValidationError(detail=_("User does not exist."))
    if user.password != token:
        raise ValidationError(detail=_("Invalid token."))
    if password is None:
        raise ValidationError(detail=_("Password field cannot be empty."))
    if confirm_password is None:
        raise ValidationError(detail=_("Confirm password field cannot be empty."))
    if password != confirm_password:
        raise ValidationError(detail=_("Password and confirm password fields do not match."))
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise ValidationError(detail=_("Could not validate your password."))
    user.set_password(password)
    user.save()

    return True

@transaction.atomic
def change_password(*, user: User, old_password:str, new_password: str) -> PortalUser:
    """
    Changes password of a user.
    """
    if not user.check_password(old_password):
        raise ValidationError(detail=_("Old password is incorrect."))
    if new_password is None:
        raise ValidationError(detail=_("New password field cannot be empty."))
    try:
        validate_password(new_password)
    except DjangoValidationError as e:
        raise ValidationError(e.messages[0])
    try:
        user.set_password(new_password)
        user.full_clean()
    except DjangoValidationError as e:
        raise DjangoValidationError(e.messages[0])
    user.save()
    return user


@transaction.atomic
def email_confirmation_token_send(*, email: str) -> EmailConfirmationToken:
    """
    Sends email confirmation to the given email
    """
    user = user_get_from_email(email=email.lower())
    if user is None:
        raise ValidationError(detail=_("User with the given email does not exist."))
    generated_token = get_random_string(length=64)

    token = EmailConfirmationToken(token=generated_token, user=user, email=email.lower())
    token.full_clean()
    token.save()

    username = get_username_from_user(user=user)

    send_email_confirmation(token=generated_token, receiver_email=email, username=username)

    return token, status.HTTP_200_OK

@transaction.atomic
def confirmation_email_resend(*, user: PortalUser, email: Optional[str] = None) -> EmailConfirmationToken:
    """
    Resends confirmation to the given user. Returns 401 if a token object does not already exist.
    """
    email_confirmation_token = email_confirmation_token_get_from_user(user=user)
    if email_confirmation_token is not None:
        email_confirmation_token.delete()
    
    logger.error(f"Resending confirmation email to {user.email}")

    if email is None:
        email = user_email_get_from_user(user=user)
        if email is None:
            raise ValidationError(detail=_("User does not have an email."))

    if user.is_verified:
        raise ValidationError(detail=_("User already verified"))
    
    generated_token = get_random_string(length=64)

    confirmation_token = EmailConfirmationToken(token=generated_token, user=user, email=email.lower())
    confirmation_token.full_clean()
    confirmation_token.save()
    
    username = get_username_from_user(user=user)
    token = send_email_confirmation(token=generated_token, receiver_email=email, username=username)
    return confirmation_token


@transaction.atomic
def user_verify(*, user:PortalUser, token: str) -> PortalUser:
    """
    Verifies the user if the given confirmation token is valid
    """
    token_object = token_get_from_user_and_incoming_token(user=user, incoming_token=token)
    if token_object is None:
        raise ValidationError(detail=_("Confirmation link is invalid."))
    print(token_object.has_expired)
    if token_object.has_expired:
        token_object.delete()
        raise ValidationError(detail=_("Confirmation email has expired. Please request a new confirmation email."))

    token_email = token_object.email
    user.is_verified = True
    user.full_clean()
    user.save(update_fields=["is_verified"])
    token_object.delete()

    return user

@transaction.atomic
def profile_picture_change(*, uid: str, user: User) -> PortalUser:
    """
    Replaces the current profile picture of a given user with the image associated with the uid.
    """
    picture = profile_picture_get_from_uid(uid=uid)
    if picture is None:
        return ValidationError(detail=_("Invalid uid, image does not exist."))
    user.profile_picture = picture
    user.save(update_fields=["profile_picture"])

    return user


@transaction.atomic
def change_email_address_token_send(*, user:PortalUser) -> EmailConfirmationToken:
    """
    Sends email confirmation to the given email
    """
    pass


@transaction.atomic
def batch_create_users(users: List[dict]) -> List[PortalUser]:
    """
    Batch creates users and returns a list of PortalUser objects.
    """
    created_users = []

    def create_user(user_data):
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']
        user_type = user_data['user_type']
        full_name = user_data['full_name']

        verification_status = True

        # Check for existing user and raise a validation error.
        existing_user = check_if_email_is_taken(email=email.lower())
        if existing_user:
            raise DjangoValidationError(_("User with the email already exists."))
        
        existing_username = user_get_from_username(username=username.lower())
        if existing_username is not None:
            raise DjangoValidationError(f"User with the username `{username}` already exists.")

        user = User(
            full_name=full_name,
            username=username.lower(),
            email=email.lower(),
            is_verified=verification_status,
        )

        try:
            user.set_password(password)
            user.full_clean()
            user.save()
        except DjangoValidationError as e:
            raise DjangoValidationError(e.messages[0])

        # Assign user role
        try:
            user_role = get_user_role_by_name(user_type=user_type)
            user.roles.add(user_role)
            user.save()
        except UserRoles.DoesNotExist:
            raise DjangoValidationError(detail=_("User role does not exist."))

        return user

    # Using ThreadPoolExecutor to create users asynchronously
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(create_user, user_data) for user_data in users]

        for future in as_completed(futures):
            try:
                created_user = future.result()
                created_users.append(created_user)
            except Exception as e:
                # Handle exceptions raised during user creation
                print(f"Error creating user: {str(e)}")

    return created_users