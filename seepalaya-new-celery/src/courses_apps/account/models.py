from datetime import datetime, timedelta
from config.model_mixins import IdentifierTimeStampAbstractModel
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.db.models import Index, Q
from django.db.models.constraints import UniqueConstraint
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _
from config.validators import validate_full_name
from django.core.validators import MinLengthValidator

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, username, password, **extra_fields)
    
class ProfilePicture(IdentifierTimeStampAbstractModel):
    name = models.CharField(max_length=50)
    link = models.URLField(verbose_name="Profile picture link")

    def __str__(self) -> str:
        return self.name
    
class UserRoles(IdentifierTimeStampAbstractModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = "User Roles"

class PortalUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(
        max_length=60,
        null=True, 
        blank=True, 
        validators=[
            validate_full_name,
            MinLengthValidator(5, message="Full name must be at least 5 characters long.")
        ]
    )
    address = models.CharField(max_length=60, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ForeignKey(
        ProfilePicture,
        on_delete=models.PROTECT,
        related_name="user",
        blank=True,
        null=True,
    )
    roles = models.ManyToManyField(UserRoles, related_name="users_roles")

    objects = UserManager()
    USERNAME_FIELD = "username"

    def get_full_name(self) -> str:
        return self.full_name
    
    def __str__(self):
        return self.username


class EmailConfirmationToken(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_confirmation_token")
    created_time = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=64)
    email = models.EmailField(max_length=255, null=True)

    class Meta:
        verbose_name = "Email Confirmation Token"
        verbose_name_plural = "Email Confirmation Tokens"
        ordering = ["-created_time"]

    def __str__(self):
        return self.user.username + self.email
    
    @property
    def has_expired(self) -> bool:
        now = timezone.now()
        expiry_time = self.created_time + timedelta(minutes=5)
        return now > expiry_time
    

# class EmailAddress(IdentifierTimeStampAbstractModel):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_addresses")
#     email = models.EmailField(max_length=255)
#     verified = models.BooleanField(default=False)
#     primary = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = "Email Address"
#         verbose_name_plural = "Email Addresses"
#         unique_together = ["user", "email"]
#         constraints = [
#                 UniqueConstraint(
#                     fields=["email"],
#                     name="unique_verified_email",
#                     condition=Q(verified=True),
#                 )
#             ]
#         indexes = [Index(Upper("email"), name="account_emailaddress_upper")]

#     def __str__(self):
#         return self.email


class ChangeEmailAddressToken(IdentifierTimeStampAbstractModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_change_token")
    created_time = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=64)
    email = models.EmailField(max_length=255, null=True)

    class Meta:
        verbose_name = "Email Change Token"
        verbose_name_plural = "Email Change Tokens"
        ordering = ["-created_time"]

    def __str__(self):
        return self.user.username + self.email
    
    @property
    def has_expired(self) -> bool:
        now = timezone.now()
        created_time = self.created_time + timedelta(minutes=5)
        return now > created_time
    