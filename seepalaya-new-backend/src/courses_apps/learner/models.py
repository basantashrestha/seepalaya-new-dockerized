from django.db import models
from courses_apps.account.models import PortalUser
 
class Learner(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE, related_name="learner")
    date_of_birth = models.DateField(null=True, blank=True)
    pin = models.CharField(max_length=6, null=True, blank=True)
    total_points = models.IntegerField(blank=True, null=True)
    account_maintained_by = models.CharField(max_length=20, choices=[
        ('LEARNER', 'Learner'),
        ('GUARDIAN', 'Guardian'),
        ('TEACHER', 'Teacher'),
    ], default='LEARNER')

    class Meta:
        verbose_name = "Learner"
        verbose_name_plural = "Learners"

    def __str__(self):
        return self.user.username