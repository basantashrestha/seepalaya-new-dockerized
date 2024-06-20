from django.db import models
from courses_apps.account.models import PortalUser
from courses_apps.learner.models import Learner

    
class Guardian(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE, related_name="guardian")
    children = models.ManyToManyField(Learner, related_name="guardian")

    class Meta:
        verbose_name = "Guardian"
        verbose_name_plural = "Guardians"

    def __str__(self):
        return self.user.username