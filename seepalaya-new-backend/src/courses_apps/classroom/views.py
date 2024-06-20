import csv
import os
from typing import List
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from courses_apps.account.permissions import IsTeacher
from .services import (
    create_classroom, 
    student_create,
    join_classroom,
    add_students_to_classroom,
    remove_students_from_classroom,
    update_classroom,
    delete_classroom
)
from .selectors import (
    get_classroom_students,
    get_classroom_details,
    get_class_room_name_from_class_code
)
from .nested_serializers import TeacherStudentCreationInputNestedSerializer, TeacherStudentCreationOutputNestedSerializer
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from gettext import gettext as _
from drf_spectacular.utils import extend_schema
from .tasks import delete_student_detail_csv
import asyncio
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

class CreateClassRoomAPIView(APIView):
    """
    This view is used to create a classroom.

    Methods:
    - post: Handles the HTTP POST request to create a new classroom.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class CreateClassRoomInputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True)

    class CreateClassRoomOutputSerializer(serializers.Serializer):
        title = serializers.CharField(read_only=True)
        class_code = serializers.CharField(read_only=True)
        teacher = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request to create a new classroom.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object with the created classroom details.

        Raises:
        - DjangoValidationError: If there is a validation error in creating the classroom.
        - ValidationError: If there is a validation error in creating the classroom.
        """

        input_serializer = self.CreateClassRoomInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            class_details = create_classroom(
                **input_serializer.validated_data,
                teacher=request.user.teacher
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

        output_serializer = self.CreateClassRoomOutputSerializer(class_details)
        return Response({
            "success": True,
            "message": _("Classroom created successfully."),
            "data": output_serializer.data
        }, status=status.HTTP_201_CREATED)

class GetClassRoomDetailsAPIView(APIView):
    """
    API view to get details of a classroom.

    This view requires the user to be authenticated and a teacher.
    It expects a POST request with the 'class_code' parameter in the request data.

    The response will include the title, class code, and student count of the classroom.

    If any validation errors occur, appropriate error responses will be returned.

    Example usage:
    ```
    POST /api/classroom/details/
    {
        "class_code": "ABC123"
    }
    ```

    Example response:
    ```
    {
        "success": True,
        "message": "Classroom details fetched successfully.",
        "data": {
            "title": "Mathematics",
            "class_code": "ABC123",
            "student_count": 25
        }
    }
    ```
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class GetClassRoomDetailsInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)

    class GetClassRoomDetailsOutputSerializer(serializers.Serializer):
        title = serializers.CharField()
        class_code = serializers.CharField()
        student_count = serializers.IntegerField()

    @transaction.atomic
    def post(self,  request, *args, **kwargs):
        input_serializer = self.GetClassRoomDetailsInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        teacher_user = request.user

        try:
            class_details = get_classroom_details(
                **input_serializer.validated_data,
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
        
        output_serializer = self.GetClassRoomDetailsOutputSerializer(class_details)
        return Response({
            "success": True,
            "message": _("Classroom details fetched successfully."),
            "data": output_serializer.data
        }, status=status.HTTP_200_OK
        )
    

class ClassRoomUpdateAPIView(APIView):
    """
    API view for updating a classroom.

    This view allows authenticated teachers to update the details of a classroom.
    The request should include the class code and the new title for the classroom.

    Methods:
    - post: Handles the POST request for updating the classroom.

    Attributes:
    - permission_classes: A list of permission classes required for accessing this view.
    - ClassRoomUpdateInputSerializer: Serializer class for validating the input data.
    - ClassRoomUpdateOutputSerializer: Serializer class for serializing the output data.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class ClassRoomUpdateInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)
        title = serializers.CharField(required=True)
    
    class ClassRoomUpdateOutputSerializer(serializers.Serializer):
        title = serializers.CharField()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for updating the classroom.

        This method validates the input data, updates the classroom details,
        and returns the updated classroom details in the response.

        Args:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object with the updated classroom details.

        Raises:
        - DjangoValidationError: If there is a validation error in the input data.
        - ValidationError: If there is a validation error in the input data.
        - KeyError: If a required key is missing in the input data.
        """

        input_serializer = self.ClassRoomUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        teacher_user = request.user

        try:
            class_details = update_classroom(
                **input_serializer.validated_data,
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
        
        output_serializer = self.ClassRoomUpdateOutputSerializer(class_details)
        return Response({
            "success": True,
            "message": _("Classroom updated successfully."),
            "data": output_serializer.data
        }, status=status.HTTP_200_OK)


class DeleteClassRoomAPIView(APIView):
    """
    API view for deleting a classroom.

    This view allows authenticated teachers to delete a classroom by providing the class code.

    Methods:
    - post: Handles the HTTP POST request for deleting a classroom.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class DeleteClassRoomInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle the HTTP POST request to delete a classroom.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object.

        Raises:
            DjangoValidationError: If there is a validation error in the input data.
            ValidationError: If there is a validation error.
            KeyError: If a required key is missing.

        """
        input_serializer = self.DeleteClassRoomInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        teacher_user = request.user

        try:
            class_details = delete_classroom(
                **input_serializer.validated_data,
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

        return Response({
            "success": True,
            "message": _("Classroom deleted successfully."),
        }, status=status.HTTP_200_OK)



class TeacherStudentCreationAPIView(APIView):
    """
    This view is used to create students in bulk.

    Methods:
    - post: Handles the POST request to create students in bulk.

    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class TeacherStudentCreationInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)
        students = serializers.ListField(child=serializers.CharField(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TeacherStudentCreationOutputSerializer = TeacherStudentCreationOutputNestedSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to create students in bulk.

        Args:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object with the created students' data and a download link for the CSV file.

        """
        input_serializer = self.TeacherStudentCreationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        students_data = input_serializer.validated_data.get('students', [])
        class_code = input_serializer.validated_data.get('class_code')
        created_students = []
        failed_students = []

        teacher_user = request.user
        class_name = get_class_room_name_from_class_code(class_code)

        try:
            with transaction.atomic():
                created_students = student_create(
                    class_code=class_code,
                    students=students_data,
                    teacher_user=teacher_user.username
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

        # Serialize the created students for response and CSV
        output_serializer = self.TeacherStudentCreationOutputSerializer(
            {
                'students': created_students,
                'count': len(created_students)
            }
        )
        created_students_data = output_serializer.data['students']

        # Ensure the directory exists
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)

        # Create CSV file with a unique filename
        csv_file_path = os.path.join(media_root, f'created_students_{teacher_user}.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['username', 'full_name', 'password']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for student in created_students_data:
                writer.writerow({
                    'username': student['username'],
                    'full_name': student['full_name'],
                    'password': student['password'],
                })

        # Schedule file deletion task
        delete_student_detail_csv.apply_async((csv_file_path,), countdown=900)

        # Provide download link
        file_url = default_storage.url(f'created_students_{teacher_user}.csv')

        response_data = {
            "success": True,
            "message": "Students added successfully",
            "data": output_serializer.data,
            'class_name': class_name,
            "file_url": file_url
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class JoinClassRoomWithCodeAPIView(APIView):
    """
    This view is used to join a classroom with a class code.

    Methods:
    - post: Handles the POST request to join a classroom with a class code.
    """

    permission_classes = [IsAuthenticated]

    class JoinClassRoomWithCodeInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to join a classroom with a class code.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object with the result of the join operation.
        """
        input_serializer = self.JoinClassRoomWithCodeInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            class_details = join_classroom(
                **input_serializer.validated_data,
                username=request.user
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
        return Response({
            "success": True,
            "message": _("Classroom joined successfully."),
            "data": class_details
        }, status=status.HTTP_200_OK)

class ClassStudentListAPIView(APIView):
    """
    This view is used to get the list of students in a classroom.

    Methods:
    - post: Retrieves the list of students in a classroom based on the provided input data.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class ClassStudentListInputSerializer(serializers.Serializer):
        class_code = serializers.CharField()
        search_query = serializers.CharField(required=False, allow_blank=True)
        sort_order = serializers.ChoiceField(choices=['asc', 'desc'], required=False)

    class ClassStudentListOutputSerializer(serializers.Serializer):
        full_name = serializers.CharField()
        username = serializers.CharField()
        # email = serializers.EmailField()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Retrieves the list of students in a classroom based on the provided input data.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object containing the list of students fetched successfully.
        """
        input_serializer = self.ClassStudentListInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            students_details = get_classroom_students(
                **input_serializer.validated_data,
                teacher_user=request.user
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
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = self.ClassStudentListOutputSerializer(students_details, many=True)
        return Response({
            "success": True,
            "message": _("Students fetched successfully."),
            "data": output_serializer.data
        }, status=status.HTTP_200_OK)


class AddStudentsToClassRoomAPIView(APIView):
    """
    This view is used to add students to a classroom.

    Methods:
    - post: Handles the POST request to add students to a classroom.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class AddStudentsToClassRoomInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)
        students = serializers.ListField(child=serializers.CharField(), required=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to add students to a classroom.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object with the result of the operation.
        """
        input_serializer = self.AddStudentsToClassRoomInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        teacher_user = request.user

        try:
            class_details = add_students_to_classroom(
                **input_serializer.validated_data,
                teacher_user=teacher_user
            )
            print(input_serializer.validated_data)
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
        return Response({
            "success": True,
            "message": _("Students added successfully."),
            "data": class_details
        }, status=status.HTTP_200_OK)
    

class RemoveStudentsFromClassRoomAPIView(APIView):
    """
    This view is used to remove students from a classroom.

    Methods:
    - post: Handles the HTTP POST request to remove students from a classroom.
    """

    permission_classes = [IsAuthenticated, IsTeacher]

    class RemoveStudentsFromClassRoomInputSerializer(serializers.Serializer):
        class_code = serializers.CharField(required=True)
        students = serializers.ListField(child=serializers.CharField(), required=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request to remove students from a classroom.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A Response object with the success status, message, and data.
        """
        input_serializer = self.RemoveStudentsFromClassRoomInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        teacher_user = request.user

        try:
            class_details = remove_students_from_classroom(
                **input_serializer.validated_data,
                teacher_user=teacher_user
            )
            print(input_serializer.validated_data)
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
        return Response({
            "success": True,
            "message": _("Students removed successfully."),
            "data": class_details
        }, status=status.HTTP_200_OK)
    
