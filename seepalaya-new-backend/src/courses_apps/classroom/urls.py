from django.urls import path

from .views import *

app_name = "classroom"

urlpatterns = [
    path("create/", CreateClassRoomAPIView.as_view(), name="create_classroom"),
    path("details/", GetClassRoomDetailsAPIView.as_view(), name="classroom_details"),
    path("update/", ClassRoomUpdateAPIView.as_view(), name="classroom_update"),
    path("delete/", DeleteClassRoomAPIView.as_view(), name="classroom_delete"),
    path("student/create/", TeacherStudentCreationAPIView.as_view(), name="student_create"),
    path('join-class/', JoinClassRoomWithCodeAPIView.as_view(), name='join_classroom'),
    path('students/', ClassStudentListAPIView.as_view(), name='get_classroom_students'),
    path('students/add/', AddStudentsToClassRoomAPIView.as_view(), name='add_student_to_classroom'),
    path('students/remove/', RemoveStudentsFromClassRoomAPIView.as_view(), name='remove_student_from_classroom'),
]