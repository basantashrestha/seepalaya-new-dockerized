from django.db import models
from config.model_mixins import IdentifierTimeStampAbstractModel
from courses_apps.core.models import Language, Grade, Subject
from django.utils.translation import gettext_lazy as _

class EpaathModules(IdentifierTimeStampAbstractModel):
    title = models.CharField(max_length=255)
    chapter_id = models.CharField(max_length=25)
    abstract = models.TextField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    published = models.CharField(
        verbose_name=_("published"),
        max_length=3,
        default="yes",
        choices=(
            ("yes", _("Yes")),
            ("no", _("No"))
        )
    )

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("E-Paath Module")
        verbose_name_plural = _("E-Paath Modules")