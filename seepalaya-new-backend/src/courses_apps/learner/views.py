from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import ValidationError
from courses_apps.account.services import email_confirmation_token_send
from .services import learner_signup
from .selectors import student_teacher_list
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

class LearnerSignupAPIView(APIView):
    class LearnerSignupInputSerializer(serializers.Serializer):
        full_name = serializers.CharField(required=True)
        email = serializers.CharField(required=True)
        password = serializers.CharField(write_only=True, required=True)
        confirm_password = serializers.CharField(write_only=True, required=True)

    class LearnerSignupOutputSerializer(serializers.Serializer):
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
        input_serializer = self.LearnerSignupInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            learner_signup_details, refresh_token = learner_signup(
                **input_serializer.validated_data
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message
                },
                status=status.HTTP_403_FORBIDDEN,
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
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        try:
            verification = email_confirmation_token_send(email=learner_signup_details.user_email)
            print('verification sent')
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
        output_serializer = self.LearnerSignupOutputSerializer(learner_signup_details)
        response = Response(
            {
                "success": True,
                "message": "Learner signup successful",
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


class ListTeachersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class ListTeacherOutputSerializer(serializers.Serializer):
        username = serializers.CharField(read_only=True)
        email = serializers.EmailField(read_only=True)
        full_name = serializers.CharField(read_only=True)

    def get(self, request, *args, **kwargs):
        try:
            queryset = student_teacher_list(user=request.user)
            output_serializer = self.ListTeacherOutputSerializer(queryset, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Teachers list fetched successfully.",
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

