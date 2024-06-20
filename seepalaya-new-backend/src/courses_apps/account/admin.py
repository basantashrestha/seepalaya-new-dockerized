from django.contrib import admin
from .models import PortalUser,UserRoles, ProfilePicture

admin.site.register(PortalUser)
admin.site.register(UserRoles)
admin.site.register(ProfilePicture)
