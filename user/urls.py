from django.urls import path

from user.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    VerifyEmailView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="user-email-verify"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="user-password-reset"),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="user-password-reset-confirm-post",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="user-password-reset-confirm",
    ),
]
