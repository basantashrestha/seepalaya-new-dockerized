from django.contrib import admin
from .models import EpaathModules

class EpaathModulesAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter_id', 'language', 'grade', 'subject', 'published')
    list_filter = ('language', 'grade', 'subject', 'published')
    search_fields = ('title', 'chapter_id', 'link')
    ordering = ('title', 'chapter_id', 'abstract', 'thumbnail', 'link', 'language', 'grade', 'subject', 'published')

admin.site.register(EpaathModules, EpaathModulesAdmin)
