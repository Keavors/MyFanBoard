from django.urls import path
from .views import (
    UserRegisterView,
    UserVerifyRegistrationCodeView,
    UserLoginRequestCodeView,
    UserLoginVerifyCodeView,
    UserLogoutView
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-registration-code/', UserVerifyRegistrationCodeView.as_view(), name='verify_registration_code'),
    path('login/', UserLoginRequestCodeView.as_view(), name='login_request_code'), # Для запроса кода входа
    path('verify-login-code/', UserLoginVerifyCodeView.as_view(), name='verify_login_code'), # Для ввода кода входа
    path('logout/', UserLogoutView.as_view(), name='logout'),
]