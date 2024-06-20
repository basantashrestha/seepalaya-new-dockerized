from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError
from courses_apps.teacher.models import Teacher
from courses_apps.account.models import PortalUser
from courses_apps.learner.models import Learner
from django.db.models import F
from django.contrib.postgres.aggregates import ArrayAgg
from django.utils.translation import gettext as _

User = get_user_model()

def student_teacher_list(*, user: PortalUser) -> QuerySet:
    """
    Returns a list of teachers for a given learner email, including the created_by field.
    """
    try:
        learner = Learner.objects.get(user=user)
    except Learner.DoesNotExist:
        raise ValidationError(_("Learner does not exist."))

    queryset = (
        learner.teacher.prefetch_related("user") 
        .annotate(
            full_name=F("user__full_name"),
            username=F("user__username"),
            email=F("user__email"),
        )
        .values("full_name", "username", "email")
    )

    return queryset
