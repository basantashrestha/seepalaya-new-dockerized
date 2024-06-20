from dataclasses import dataclass
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from courses_apps.account.services import user_signup
from .models import Learner
from courses_apps.account.helpers import construct_username_from_email
from datetime import date
from courses_apps.account.selectors import check_verification_requirement, get_user_roles_by_user

@transaction.atomic
def learner_signup(
    *,
    full_name: str, 
    # username: str, 
    email: str,
    # date_of_birth: date,
    password: str, 
    confirm_password: str
) -> object:
    """
    Signs up and returns a LearnerSignupDetails dataclass object.
    Sends email confirmation after the signup is complete.
    """
    @dataclass(frozen=True)
    class LearnerSignupDetails:
        user_type: str
        username: str
        full_name: str
        user_email: str
        is_verified: bool
        access_token: str
        staff: bool
        superuser: bool
        verification_required: bool

    user_type = "learner"
    created_by="LEARNER"
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
        learner = Learner(user=user,)
        learner.full_clean()
    except DjangoValidationError as e:
        raise ValidationError(detail=_(str(e)))
    
    learner.save()

    token = RefreshToken.for_user(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    is_verified = user.is_verified
    user_type = get_user_roles_by_user(user=user)
    staff = False
    superuser = False
    user_email = user.email
    verification_required = check_verification_requirement(user=user)

    signup_details = LearnerSignupDetails(
        user_type, username, full_name, user_email, is_verified, access_token, staff, superuser, verification_required
    )

    return signup_details, refresh_token