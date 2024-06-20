from typing import List
import random
import string
import re
from django.contrib.auth import get_user_model

User = get_user_model()

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
        random_chars = ''.join(random.choices(string.ascii_letters, k=2)) + ''.join(random.choices(string.digits, k=2))
        final_username = f"{username[:5]}_{random_chars}"

    return final_username