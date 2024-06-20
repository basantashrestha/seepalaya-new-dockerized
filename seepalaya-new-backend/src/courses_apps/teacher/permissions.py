from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class IsTeacher(BasePermission):
    """
    Global permission check for users who are teachers.
    """
    message = "User needs to be a teacher to access this view."

    def has_permission(self, request, view):
        return User.objects.filter(roles__name="teacher", pk=request.user.pk).exists()