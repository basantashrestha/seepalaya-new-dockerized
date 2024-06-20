import re
import random
import string
import secrets
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .tasks import send_email_task

User = get_user_model()

def send_email_confirmation(*, token: str, receiver_email: str, username: str) -> bool:
    data ={
        'token':token
    }
    message = f'press here http://192.168.5.22:3000/account/confirm-email/{username}/{token}'
    subject='Please, confirm your email address for seepalaya.olenepal.org.'
    email_to = receiver_email
    # send_mail(subject, message, email_from, [email_to], fail_silently=False)
    send_email_task.delay(subject, message, email_to)
    print(message)
    print('email sent')
    return True

def identify_email_or_username(credential: str) -> bool:
    # Regular expression to match email pattern
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, credential):
        return "email"
    return "username"

def send_reset_password_link(*, link: str, receiver_email: str) -> bool:
    """
    Sends a reset password link to the provided email
    """
    subject = "Password reset link"
    message = f"Your link is {link}"
    email_from = settings.EMAIL_HOST
    email_to = receiver_email

    # send_mail(subject, message, email_from, [email_to], fail_silently=False)
    send_email_task.delay(subject, message, email_to)
    print(message)
    return True


def construct_username_from_email(email: str) -> str:
    """
    Constructs a unique username from the given email, handling potential duplicates
    and special characters.
    """
    username = re.sub(r"[^\w]", "", email.split("@")[0].lower())

    # Ensure the username is no longer than 10 characters
    username = username[:10]

    # Check if the username already exists in the database
    final_username = username
    while User.objects.filter(username__startswith=final_username).exists():
        # Generate a random string of 2 letters and 2 numbers
        random_chars = ''.join(random.choices(string.ascii_letters, k=1)) + ''.join(random.choices(string.digits, k=2))
        final_username = f"{username[:5]}_{random_chars}"

    return final_username


def construct_username_from_full_name(full_name: str) -> str:
    """
    Constructs a unique username from the given full name, handling potential duplicates
    and special characters.
    """
    username = re.sub(r"[^\w]", "", full_name.lower())

    username = username[:10]

    final_username = username
    while User.objects.filter(username__startswith=final_username).exists():
        # Generate a random string of 2 letters and 2 numbers
        random_chars = ''.join(random.choices(string.ascii_letters, k=1)) + ''.join(random.choices(string.digits, k=2))
        final_username = f"{username[:5]}_{random_chars}"

    return final_username


def construct_email_from_username(username: str) -> str:
    """
    Constructs a unique email address from the given username, handling potential duplicates.
    """
    email = f"{username}@seepalaya.com"
    final_email = email
    # while EmailAddress.objects.filter(email=final_email).exists():
    #     random_chars = ''.join(random.choices(string.ascii_letters, k=2))
    #     final_email = f"{email[:5]}_{random_chars}@seepalaya.com"
    while User.objects.filter(email__startswith=final_email).exists():
        random_string = ''.join(random.choices(string.ascii_lowercase, k=3))
        username_with_suffix = f"{username}_{random_string}"
        final_email = f"{username_with_suffix}@{email.split('@')[1]}" 
    return final_email


def generate_random_password() -> str:
    """
    Generates a random password with the following criteria:
    - At least 8 characters long
    - Contains at least one lowercase letter
    - Contains at least one digit
    """
    password = ''.join(secrets.choice(string.ascii_lowercase) for i in range(8))
    return password


# def check_email_verification_state(*, email:str) -> bool:
#     """
#     Checks if the email is verified or not
#     """
#     return EmailAddress.objects.filter(email=email, is_verified=True).exists()