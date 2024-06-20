from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()
    

class IsVerifiedGuardian(BasePermission):
    """
    Global permission check for users who are verified guardians.
    """
    message = "User needs to be a verified guardian to access this view."

    def has_permission(self, request, view):
        return User.objects.filter(roles__name="guardian", pk=request.user.pk, is_verified=True).exists()


class IsGuardian(BasePermission):
    """
    Global permission check for users who are guardians.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        return User.objects.filter(roles__name="guardian", pk=request.user.pk).exists()


class IsLearner(BasePermission):
    """
    Global permission check for users who are learners.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        return User.objects.filter(roles__name="learner", pk=request.user.pk).exists()


class IsTeacher(BasePermission):
    """
    Global permission check for users who are teachers.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        return User.objects.filter(roles__name="teacher", pk=request.user.pk).exists()


class IsVerified(BasePermission):

    message = "User needs to be verified to access this view."

    def has_permission(self, request, view):
        """
        Checks whether a given user has permission.
        """
        if request.user.is_verified:
            return True
        return False
