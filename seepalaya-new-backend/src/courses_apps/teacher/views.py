from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import ValidationError
from courses_apps.account.services import email_confirmation_token_send
from .services import teacher_signup, student_signup, student_update, student_delete
from .selectors import teacher_student_list, get_teacher_classroom_list
from .permissions import IsTeacher
from .nested_serializers import TeacherStudentCreationInputNestedSerializer, TeacherStudentCreationOutputNestedSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _

class TeacherSignupAPIView(APIView):
    class TeacherSignupInputSerializer(serializers.Serializer):
        # username = serializers.CharField(required=True)
        full_name = serializers.CharField(required=True)
        email = serializers.EmailField(required=True)
        password = serializers.CharField(write_only=True, required=True)
        confirm_password = serializers.CharField(write_only=True, required=True)

    class TeacherSignupOutputSerializer(serializers.Serializer):
        username = serializers.CharField(read_only=True)
        user_email = serializers.EmailField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        is_verified = serializers.BooleanField(read_only=True)
        verification_required = serializers.BooleanField(read_only=True)
        user_type = serializers.ListField(child=serializers.CharField(), read_only=True)
        staff = serializers.BooleanField(read_only=True)
        superuser = serializers.BooleanField(read_only=True)
        access_token = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.TeacherSignupInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            teacher_signup_details, refresh_token = teacher_signup(
                **input_serializer.validated_data
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            verification = email_confirmation_token_send(email=teacher_signup_details.user_email)
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        output_serializer = self.TeacherSignupOutputSerializer(teacher_signup_details)
        response = Response(
            {
                "success": True,
                "message": "Teacher signup successful",
                "data": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.REFRESH_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",
            secure=False,
        )
        print("Refresh token set successfully.")
        print(refresh_token)

        return response
    

class TeacherGetClassRoomListAPIView(APIView):
    """
    API view to get a list of classrooms for a teacher user.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class TeacherGetClassRoomListInputSerializer(serializers.Serializer):
        exclude_class_code = serializers.CharField(required=False, allow_blank=True)

    class TeacherGetClassRoomListOutputSerializer(serializers.Serializer):
        classroom_title = serializers.CharField()
        classroom_code = serializers.CharField()
        student_count = serializers.IntegerField()
        
    def post(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve the list of classrooms.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response containing the list of classrooms.

        Raises:
            DjangoValidationError: If there is a validation error in the Django framework.
            ValidationError: If there is a validation error.
            KeyError: If a key error occurs.
            Exception: If any other exception occurs.
        """
        input_serializer = self.TeacherGetClassRoomListInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        exclude_class_code = input_serializer.validated_data.get("exclude_class_code", "")
        teacher_user = request.user

        try:
            queryset = get_teacher_classroom_list(
                exclude=exclude_class_code,
                teacher_user=teacher_user
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError as e:
            return Response(
                {
                    "success": False,
                    "message": e
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = self.TeacherGetClassRoomListOutputSerializer(queryset, many=True)
        return Response({
            "success": True,
            "message": _("Classes fetched successfully."),
            "data": output_serializer.data
        }, status=status.HTTP_200_OK)


class TeacherStudentCreationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TeacherStudentCreationInputSerializer = (
            TeacherStudentCreationInputNestedSerializer
        )
        self.TeacherStudentCreationOutputSerializer = (
            TeacherStudentCreationOutputNestedSerializer
        )

    @extend_schema(
        request={200: TeacherStudentCreationInputNestedSerializer},
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.TeacherStudentCreationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        students_data = input_serializer.validated_data.get('students', [])
        created_students = []
        failed_students = []
        
        teacher_user = request.user
        
        for student_data in students_data:
            try:
                student_signup_details = student_signup(
                    teacher_user=teacher_user,
                    full_name=student_data['full_name'],
                    username=student_data['username'],
                    password=student_data['password']
                )
                created_students.append(student_signup_details)
            except ValidationError as e:
                return Response(
                    {
                        "success": False,
                        "message": e.detail[0]
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except KeyError as e:
                failed_students.append(student_data)

        output_serializer = self.TeacherStudentCreationOutputSerializer({'students': created_students})
        response_data = {
            "success": True,
            "message": "Students added successfully",
            "data": output_serializer.data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class StudentListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    class StudentListOutputSerializer(serializers.Serializer):
        student_full_name = serializers.CharField()
        student_username = serializers.CharField()
        student_maintained_by = serializers.CharField()
        classroom = serializers.CharField()
        # email = serializers.EmailField()

    def get(self, request, *args, **kwargs):
        try:
            queryset = teacher_student_list(user=request.user)
            output_serializer = self.StudentListOutputSerializer(queryset, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Students list fetched successfully",
                    "data": output_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UpdateStudentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    class UpdateStudentIntputSerializer(serializers.Serializer):
        student_username = serializers.CharField(required=True)
        full_name = serializers.CharField(required=False)
        username = serializers.CharField(required=False)
        password = serializers.CharField(required=False)
        
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.UpdateStudentIntputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            child = student_update(
                user=request.user,
                **input_serializer.validated_data
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message":str(e.detail[0]) if isinstance(e, ValidationError) else str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": True,
            "message": "Student updated successfully."
        }, status=status.HTTP_200_OK)
    

class DeleteStudentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    class DeleteStudentInputSerializer(serializers.Serializer):
        student_username = serializers.CharField()

    def post(self, request, *args, **kwargs):
        input_serializer = self.DeleteStudentInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            remove_student = student_delete(user=request.user, **input_serializer.validated_data)
        except ValidationError as e:
           return Response({
                "success": False,
                "message": str(e.detail[0]) if isinstance(e, ValidationError) else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": True,
            "message": "Student deleted successfully."
        }, status=status.HTTP_200_OK)