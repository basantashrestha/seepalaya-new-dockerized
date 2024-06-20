from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class IsGuardian(BasePermission):
    """
    Global permission check for users who are guardians.
    """
    message = "User needs to be a guardian to access this view."

    def has_permission(self, request, view):
        return User.objects.filter(roles__name="guardian", pk=request.user.pk).exists()

