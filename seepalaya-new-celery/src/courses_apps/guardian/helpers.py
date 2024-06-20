from typing import List
import random
import string
from courses_apps.account.models import EmailAddress
from courses_apps.account.models import PortalUser

def construct_email_for_child(*, username: str, email: str) -> str:
    """
    Constructs an email for a child user based on the guardian's email/teacher's email and the child's username.
    """
    child_email = f"{username}@{email.split('@')[1]}"

    final_email = child_email
    while EmailAddress.objects.filter(email__startswith=final_email).exists():
        random_string = ''.join(random.choices(string.ascii_lowercase, k=3))
        username_with_suffix = f"{username}_{random_string}"
        final_email = f"{username_with_suffix}@{email.split('@')[1]}"

    return final_email
