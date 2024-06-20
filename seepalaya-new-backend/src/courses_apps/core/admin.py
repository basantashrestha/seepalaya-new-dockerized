from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Language, Subject, Grade

admin.site.register(Language)
admin.site.register(Subject)
admin.site.register(Grade)