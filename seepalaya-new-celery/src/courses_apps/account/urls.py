from django.urls import path

from .views import *

app_name = "account"


urlpatterns = [

    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", RotateAccessTokenAPIView.as_view(), name="refresh_token"),

    path("user-details/", GetUserDetailsAPIView.as_view(), name="user_details"),

    path("profile-pictures/all/", GetAllProfilePictureAPIView.as_view(), name="get_all_profile_pictures"),
    path("profile-picture/update/", ChangeProfilePictureAPIVIew.as_view(), name="update_profile_picture"),


    path("email/confirmation/", UserEmailVerification.as_view(), name="user_email_conmfirmation"),
    path("resend-email-confirmation/", ResendEmailConfirmationAPIView.as_view(), name="resend_email_confirmation"),

    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="reset_password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset_password"),
    path("password/change/", ChangePasswordAPIView.as_view(), name="change_password"),

    # path("add-secondary-email/", UserAddSecondaryEmailAddressesAPIView.as_view(), name="add_secondary_email"),
    # path("switch-primary-email/", SwitchPrimaryUserEmailAPIView.as_view(), name="switch_primary_email"),
    # path("remove-secondary-email/", RemoveSecondaryUserEmailAPIView.as_view(), name="remove_secondary_email"),

]