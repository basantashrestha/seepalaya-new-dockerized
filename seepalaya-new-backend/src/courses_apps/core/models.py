from django.db import models
from django.utils.translation import gettext_lazy as _
from config.model_mixins import IdentifierTimeStampAbstractModel

class Language(IdentifierTimeStampAbstractModel):
    language = models.CharField(max_length=11, verbose_name=_("Language"))
    abbreviation = models.CharField(max_length=3, verbose_name=_("Abbreviation"))

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Language")

    def __str__(self):
        return self.language

class Subject(IdentifierTimeStampAbstractModel):
    subject = models.CharField(max_length=50, verbose_name=_("Subject"))

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subject")

    def __str__(self):
        return self.subject

class Grade(IdentifierTimeStampAbstractModel):
    grade = models.CharField(max_length=11, verbose_name=_("Grade"))
    in_symbol = models.CharField(max_length=3, verbose_name=_("Grade in Symbol"))

    class Meta:
        verbose_name = _("Grade")
        verbose_name_plural = _("Grade")

    def __str__(self):
        return self.grade + " (" + self.in_symbol + ")"