from django.urls import path

from .views import *

app_name = "learner"

urlpatterns = [
    path("signup/", LearnerSignupAPIView.as_view(), name="learner_signup"),

    path("teacher/list/", ListTeachersAPIView.as_view(), name="student_teacher_list"),

]