from django.urls import path

from .views import *

app_name = "teacher"

urlpatterns = [
    path("signup/", TeacherSignupAPIView.as_view(), name="teacher_signup"),

    path("classroom/list/", TeacherGetClassRoomListAPIView.as_view(), name="classroom_list"),

    path("student/create/", TeacherStudentCreationAPIView.as_view(), name="student_create"),
    path("students/list/", StudentListAPIView.as_view(), name="students_list"),
    path("student/update/", UpdateStudentAPIView.as_view(), name="student_update"),
    path("student/delete/", DeleteStudentAPIView.as_view(), name="student_delete"),
]

