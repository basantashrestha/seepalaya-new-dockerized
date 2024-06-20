from django.db import models
from config.model_mixins import IdentifierTimeStampAbstractModel
from courses_apps.learner.models import PortalUser
from courses_apps.teacher.models import Teacher
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from config.validators import validate_class_room_name

User = get_user_model()

class ClassRoom(IdentifierTimeStampAbstractModel):
    title = models.CharField(
        max_length=255, 
        validators=[
            validate_class_room_name,
            MinLengthValidator(5, message="Classroom title must be at least 5 characters long.")
        ]
    )
    class_code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    students = models.ManyToManyField(User, related_name='classes')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')
    

