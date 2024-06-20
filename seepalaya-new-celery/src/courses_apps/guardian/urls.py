from django.urls import path

from .views import *

app_name = "guardian"

urlpatterns = [
    path("signup/", GuardianSignupAPIView.as_view(), name="guardian_signup"),

    path("child/create/", GuardianChildCreationAPIView.as_view(), name="child_create"),
    path("children/list/", ChildListAPIView.as_view(), name="children_list"),
    path("child/update/", UpdateChildAPIView.as_view(), name="child_update"),
    path("child/delete/", DeleteChildAPIView.as_view(), name="child_delete")

]