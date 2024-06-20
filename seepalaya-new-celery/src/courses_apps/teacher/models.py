from django.db import models
from courses_apps.account.models import PortalUser
from courses_apps.learner.models import Learner
from django.contrib.auth import get_user_model

User = get_user_model()

class Teacher(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE, related_name="teacher")
    school = models.CharField(max_length=255, blank=True, null=True)
    students = models.ManyToManyField(User, related_name="teacher_student")

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        return self.user.username