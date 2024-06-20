import random
import string
import logging
from django.db import DatabaseError
from .models import ClassRoom
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
import re
import secrets
from django.db.models import Q
from typing import Dict, List

User =get_user_model()

logger = logging.getLogger(__name__)

def generate_random_code(length=9):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_code_unique(code):
    try:
        return not ClassRoom.objects.filter(class_code=code).exists()
    except DatabaseError as e:
        logger.error(f"Database error occurred while checking class code uniqueness: {e}")
        raise

def generate_class_code():
    try:
        while True:
            new_code = generate_random_code()
            if is_code_unique(new_code):
                return new_code
    except Exception as e:
        logger.error(f"Error occurred while generating class code: {e}")
        raise

def generate_random_password() -> str:
    """
    Generates a random password with the following criteria:
    - At least 8 characters long
    - Contains at least one lowercase letter
    - Contains at least one digit
    """
    password = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    return password

def generate_usernames_emails_and_passwords(full_names: List[str]) -> List[Dict[str, str]]:
    """
    Constructs unique usernames, valid emails, and passwords from the given full names.
    The function operates on a list of full names.
    """
    final_usernames = []
    final_emails = []
    passwords = []

    # Prepare sets for existing usernames and emails
    existing_usernames = set(User.objects.values_list('username', flat=True))
    existing_emails = set(User.objects.values_list('email', flat=True))

    # Generate initial usernames, emails, and passwords without conflicts
    for full_name in full_names:
        if len(full_name) < 5:
            raise ValueError(f"Full name '{full_name}' must be at least 5 characters long.")

        username_base = re.sub(r"[^\w]", "", full_name.lower())[:10]
        email_base = f"{username_base}@seepalaya.com"

        # Generate unique username
        username = username_base
        while username in existing_usernames or User.objects.filter(username__startswith=username).exists():
            # Generate a random string of 2 letters and 2 numbers
            random_chars = ''.join(random.choices(string.ascii_lowercase, k=2)) + ''.join(random.choices(string.digits, k=2))
            username = f"{username_base[:5]}_{random_chars}"

        final_usernames.append(username)
        existing_usernames.add(username)

        # Generate unique email
        email = email_base
        while email in existing_emails or User.objects.filter(email=email).exists():
            # Append a random string to the email if it already exists
            random_string = ''.join(random.choices(string.ascii_lowercase, k=3))
            email = f"{username_base}_{random_string}@seepalaya.com"

        final_emails.append(email)
        existing_emails.add(email)

        # Generate password
        password = generate_random_password()
        passwords.append(password)

    return [{'full_name': fn, 'username': un, 'email': em, 'password': pw}
            for fn, un, em, pw in zip(full_names, final_usernames, final_emails, passwords)]

