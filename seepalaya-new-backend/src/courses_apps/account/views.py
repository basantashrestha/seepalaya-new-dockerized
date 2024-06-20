from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .services import (
    user_verify, confirmation_email_resend,
    user_login, user_send_forgot_password_email, 
    user_reset_password, change_password,
    profile_picture_change
)
from .selectors import (
    get_user_details, all_profile_pictures_get
)
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.middleware.csrf import get_token

User = get_user_model()


class UserLoginAPIView(APIView):
    class UserLoginInputSerializer(serializers.Serializer):
        username_or_email = serializers.CharField(write_only=True)
        password = serializers.CharField(write_only=True)

    class UserLoginOutputSerializer(serializers.Serializer):
        username = serializers.CharField(read_only=True)
        user_email = serializers.EmailField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        is_verified = serializers.BooleanField(read_only=True)
        verification_required = serializers.BooleanField(read_only=True)
        user_type = serializers.ListField(child=serializers.CharField(), read_only=True)
        staff = serializers.BooleanField(read_only=True)
        superuser = serializers.BooleanField(read_only=True)
        access_token = serializers.CharField(read_only=True)

    def post(self, request, *args, **kwargs):
        input_serializer = self.UserLoginInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            login_details, refresh_token = user_login(
                **input_serializer.validated_data
            )
        except DjangoValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.message,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": e.detail[0],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        output_serializer = self.UserLoginOutputSerializer(login_details)
        response = Response(
            {
                "success": True,
                "message": "User log in successful.",
                "data": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.REFRESH_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",
            secure=False,
        )

        return response
    
class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try: 
            # refresh_token = request.COOKIES.get("refresh_token")
            # if refresh_token is not None:
            refresh = RefreshToken(request.COOKIES.get("refresh_token"))
            refresh.blacklist()
            response = Response(
                {
                    "success": True,
                    "message": "Logout successful.",
                },
                status=status.HTTP_200_OK,
            )
            response.delete_cookie("refresh_token")
            return response
        except KeyError:
            return Response(
                {
                    "success": False,
                    "message": "No refresh token: keyerror",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class RotateAccessTokenAPIView(APIView):
    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is not None:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response(
                {
                    "success": True,
                    "message": "Token refreshed successfully.",
                    "data": {"access_token": access_token},
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "No refresh token",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

class UserInformationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        email = user.email
        is_verified = user.is_verified
        payload = {'email': email, 'is_verified': is_verified}

        return Response(data=payload, status=200)
        
class UserEmailVerification(APIView):
    permission_classes = [IsAuthenticated]

    class UserEmailVerificationInputSerializer(serializers.Serializer):
        token = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.UserEmailVerificationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_anonymous:
            return Response(
                {"success": False, "message": e.detail},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        try:
            user = user_verify(**serializer.data, user=request.user)
        except ValidationError as e:
            return Response({
                "success": False, 
                "message": e.detail[0]
            },
            status=status.HTTP_403_FORBIDDEN,
            )
        except DjangoValidationError as e:
            return Response({
                    "success": False, 
                    "message": e.message
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        return Response(
            {
                "success": True,
                "message": "User Verified Successfully.",
                "data": {"is_verified": user.is_verified},
            },
            status=status.HTTP_200_OK,
        )


class ResendEmailConfirmationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class ResendEmailConfirmationInputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)

    def post(self, request, *args, **kwargs):
        input_serializer = self.ResendEmailConfirmationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # email = input_serializer.validated_data.get('email')

        try:
            token = confirmation_email_resend(user=request.user, **input_serializer.validated_data)
        except ValidationError as e:
            return Response({
                "success": False, 
                "message": e.detail[0]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as e:
            return Response({
                "success": False, 
                "message": e.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"success": True, "message": "Confirmation email resent successfully."})

    
class ForgotPasswordAPIView(APIView):
    class ForgotPasswordInputSerializer(serializers.Serializer):
        email = serializers.EmailField()
    @extend_schema(
        request={200: ForgotPasswordInputSerializer},
    )
    def post(self, request, *args, **kwargs):
        input_serializer = self.ForgotPasswordInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            email = user_send_forgot_password_email(**input_serializer.validated_data)
        except ValidationError as e:
            return Response({
                "message": f"{e.detail[0]}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "message": "Email sent successfully."
        }, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    class ResetPasswordInputSerializer(serializers.Serializer):
        username = serializers.CharField()
        token = serializers.CharField()
        password = serializers.CharField()
        confirm_password = serializers.CharField()

    @extend_schema(
        request={200: ResetPasswordInputSerializer},
    )
    
    def post(self, request, *args, **kwargs):
        input_serializer = self.ResetPasswordInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            password_reset_status = user_reset_password(**input_serializer.validated_data)
        except Exception as e:
            return Response({
                "message": str(e.detail[0]) if isinstance(e, ValidationError) else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "message": "Password reset successful.",
        }, status=status.HTTP_200_OK)

        
class ChangePasswordAPIView(APIView):
    class ChangePasswordInputSerializer(serializers.Serializer):
        old_password = serializers.CharField()
        new_password = serializers.CharField()
    
    def post(self, request, *args, **kwargs):
        input_serializer = self.ChangePasswordInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            change_password(user=request.user, **input_serializer.validated_data)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e.detail[0]) if isinstance(e, ValidationError) else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": True,
            "message": "Password changed successfully."
        }, status=status.HTTP_200_OK)

class GetUserDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class GetUserDetailsOutputSerializer(serializers.Serializer):
        username = serializers.CharField()
        email = serializers.EmailField()
        profile = serializers.URLField()
        full_name = serializers.CharField()
        is_verified = serializers.BooleanField()
        user_type = serializers.CharField()
        account_created_by = serializers.CharField(allow_null=True)

    def get(self, request, *args, **kwargs):
        details = get_user_details(user=request.user)
        if details is not None:
            serializer = self.GetUserDetailsOutputSerializer(details)
            return Response(
                {"success": True, "message": "Request Successful", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "User does not exist"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    
class GetAllProfilePictureAPIView(APIView):
    class ProfilePictureOutputSerializer(serializers.Serializer):
        uid = serializers.UUIDField()
        link = serializers.URLField()
    
    def get(self, request, *args, **kwargs):
        pictures = all_profile_pictures_get(user=request.user)
        output_serializer = self.ProfilePictureOutputSerializer(pictures, many=True)
        return Response({
            "success": True,
            "data": output_serializer.data,
            "message": "Profile pictures fetched successfully."
        }, status=status.HTTP_200_OK)
    


class ChangeProfilePictureAPIVIew(APIView):
    permission_classes = [IsAuthenticated]

    class ProfilePictureInputSerializer(serializers.Serializer):
        uid = serializers.CharField()
    
    def post(self, request, *args, **kwargs):
        input_serializer = self.ProfilePictureInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            user = profile_picture_change(**input_serializer.validated_data, user=request.user)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": True,
            "message": "Profile picture changed successfully."
        }, status=status.HTTP_200_OK)


# class RequestChangeEmailAddressAPIView(APIView):
#     """
#     Change the email address of the user.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         try:
#             user = request.user
#             new_email = change_email_address_token_send(user=user)
#         except Exception as e:
#             return Response({
#                 "success": False,
#                 "message": str(e.detail[0]) if isinstance(e, ValidationError) else str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         return Response({
#             "success": True,
#             "message": "Email changed successfully."
#         }, status=status.HTTP_200_OK)