from django.urls import path
from .views import (
    UserRegisterView,
    UserVerifyRegistrationCodeView,
    UserLoginRequestCodeView,
    UserLoginVerifyCodeView,
    UserLogoutView
)

urlpatterns = [
    # URL для страницы регистрации пользователя.
    path('register/', UserRegisterView.as_view(), name='register'),
    # URL для страницы подтверждения кода регистрации.
    path('verify-registration-code/', UserVerifyRegistrationCodeView.as_view(), name='verify_registration_code'),
    # URL для запроса кода входа.
    path('login/', UserLoginRequestCodeView.as_view(), name='login_request_code'),
    # URL для ввода и проверки кода входа.
    path('verify-login-code/', UserLoginVerifyCodeView.as_view(), name='verify_login_code'),
    # URL для выхода пользователя из системы.
    path('logout/', UserLogoutView.as_view(), name='logout'),
]