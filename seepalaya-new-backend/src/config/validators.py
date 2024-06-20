import re
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

class NumericCharactersValidator:
    """
    Validate whether the password contains at least one numeric character.
    """
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise DjangoValidationError(
                _("The password must contain at least one numeric value."),
                code="password_no_numeric",
            )

    def get_help_text(self):
        return _("Your password must contain at least one numeric value.")

class DisallowedSpecialCharactersValidator:
    """
    Validate that the password does not contain any disallowed special characters.

    Args:
        disallowed_characters (str, optional): A string of disallowed special characters.
            If not provided, all special characters except `!@#$%^&*()_+` will be disallowed.
    """

    def __init__(self, disallowed_characters=None):
        if disallowed_characters is None:
            self.disallowed_characters = "|!#%^&*()_+-[]/{}:;\"'<>,.?\\`~"
        else:
            self.disallowed_characters = disallowed_characters

    def validate(self, password, user=None):
        for char in password:
            if char in self.disallowed_characters:
                raise DjangoValidationError(
                    self.get_error_message(char),
                    code="disallowed_character",
                )

    def get_error_message(self, disallowed_character):
        return _("The password must not contain the special character '{}'.").format(disallowed_character)

    def get_help_text(self):
        disallowed_chars_str = ", ".join(self.disallowed_characters)
        return _("Your password must not contain the following special characters: {}.").format(disallowed_chars_str)
    


def validate_full_name(value):
    message = 'Full name can only contain letters, spaces, hyphens, and apostrophes.'
    if not re.match(r'^[a-zA-Z\s\'-]+$', value):
        raise DjangoValidationError(message, params={'value': value})
    
def validate_class_room_name(value):
    message = 'Class Name can only contain letters, numbers, spaces, hyphens, and apostrophes, and cannot be completely numeric.'
    # Check for allowed characters
    if not re.match(r'^[a-zA-Z0-9\s\'-]+$', value) or value.isdigit():
        raise DjangoValidationError(message, params={'value': value})
    
    # Ensure the value is not completely numeric
    # if value.isdigit():
    #     raise DjangoValidationError('Class Name cannot be completely numeric.', params={'value': value})



