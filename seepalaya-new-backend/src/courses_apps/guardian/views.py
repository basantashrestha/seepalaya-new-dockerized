from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses_apps.guardian.services import guardian_signup
from courses_apps.account.services import email_confirmation_token_send
from django.conf import settings
from courses_apps.guardian.services import (
    child_signup, child_update, child_delete
)
from courses_apps.guardian.selectors import guardian_child_list
from courses_apps.guardian.permissions import IsGuardian
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

User = get_user_model()

class GuardianSignupAPIView(APIView):
    class GuardianSignupInputSerializer(serializers.Serializer):
        # username = serializers.CharField(required=True)
        # full_name = serializers.CharField(required=True)
        email = serializers.CharField(required=True)
        password = serializers.CharField(write_only=True, required=True)
        confirm_password = serializers.CharField(write_only=True, required=True)

    class GuardianSignupOutputSerializer(serializers.Serializer):
        user_type = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        # full_name = serializers.CharField(read_only=True)
        user_email = serializers.EmailField(read_only=True)
        is_verified = serializers.CharField(read_only=True)
        access_token = serializers.CharField(read_only=True)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.GuardianSignupInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            guardian_signup_details, refresh_token = guardian_signup(
                **input_serializer.validated_data
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            verification = email_confirmation_token_send(email=guardian_signup_details.email)
            print('verification sent')
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        output_serializer = self.GuardianSignupOutputSerializer(guardian_signup_details)
        response = Response(
            {
                "success": True,
                "message": "Guardian signup successful",
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
            secure=True,
        )
        print("Refresh token set successfully.")
        print(refresh_token)

        return response
    


class GuardianChildCreationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsGuardian]

    class GuardianChildCreationInputSerializer(serializers.Serializer):
        full_name = serializers.CharField()
        username = serializers.CharField()
        date_of_birth = serializers.DateField()
        pin = serializers.CharField()
        confirm_pin = serializers.CharField()

    class GuardianChildCreationOutputSerializer(serializers.Serializer):
        user_type = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        guardian_email = serializers.EmailField(read_only=True)
        user_email = serializers.EmailField(read_only=True)
        is_verified = serializers.CharField(read_only=True)

    @extend_schema(
        request={200: GuardianChildCreationInputSerializer},
    )

    @transaction.atomic
    def post(self, request,  *args, **kwargs):
        input_serializer = self.GuardianChildCreationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        print(input_serializer.validated_data)
        try:
            guardian_user = request.user
            child_signup_details = child_signup(
                guardian_user=guardian_user,
                **input_serializer.validated_data
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0]
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        output_serializer = self.GuardianChildCreationOutputSerializer(child_signup_details)
        response = Response(
            {
                "success": True,
                "message": "Child added successful",
                "data": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

        return response


class ChildListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsGuardian]

    class ChildListOutputSerializer(serializers.Serializer):
        full_name = serializers.CharField()
        username = serializers.CharField()
        user_type = serializers.ListField(child=serializers.CharField())
        account_creator = serializers.CharField()

    def get(self, request, *args, **kwargs):
        try:
            queryset = guardian_child_list(user=request.user)
            output_serializer = self.ChildListOutputSerializer(queryset, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Child list fetched successfully",
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


class UpdateChildAPIView(APIView):
    permission_classes = [IsAuthenticated, IsGuardian]

    class UpdateChildIntputSerializer(serializers.Serializer):
        child_username = serializers.CharField(required=True)
        # first_name = serializers.CharField(required=False)
        # last_name = serializers.CharField(required=False)
        full_name = serializers.CharField(required=False)
        username = serializers.CharField(required=False)
        pin = serializers.CharField(required=False)

    def post(self, request, *args, **kwargs):
        input_serializer = self.UpdateChildIntputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            child = child_update(
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
            "message": "Child updated successfully."
        }, status=status.HTTP_200_OK)


class DeleteChildAPIView(APIView):
    permission_classes = [IsAuthenticated, IsGuardian]

    class DeleteChildInputSerializer(serializers.Serializer):
        child_username = serializers.CharField()

    def post(self, request, *args, **kwargs):
        input_serializer = self.DeleteChildInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            remove_child = child_delete(user=request.user, **input_serializer.validated_data)
        except ValidationError as e:
           return Response({
                "success": False,
                "message": str(e.detail[0]) if isinstance(e, ValidationError) else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": True,
            "message": "Child deleted successfully."
        }, status=status.HTTP_200_OK)
    
