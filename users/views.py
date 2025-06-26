from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.views.generic import View, FormView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction

from .forms import UserRegisterForm, VerifyCodeForm, UserLoginForm
from .models import OneTimeCode

# Получение текущей активной модели пользователя Django.
User = get_user_model()

# --- Регистрация пользователя ---
class UserRegisterView(FormView):
    """
    Представление для регистрации нового пользователя.
    """
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/users/verify-registration-code/'

    def form_valid(self, form):
        """
        Обработка данных, когда форма регистрации валидна.
        Создает нового пользователя (неактивного) и генерирует одноразовый код для подтверждения.
        """
        email = form.cleaned_data['email']
        try:
            with transaction.atomic():
                # Создание нового пользователя с указанным email и именем пользователя.
                user = User.objects.create_user(email=email, username=email.split('@')[0])
                user.is_active = False # Пользователь неактивен до подтверждения Email.
                user.save()

                # Создание одноразового кода для подтверждения регистрации.
                OneTimeCode.objects.create(
                    user=user,
                    type='registration'
                )

                # Сохранение email в сессии для использования на следующем шаге.
                self.request.session['email_for_verification'] = email

            messages.success(self.request, 'Регистрация почти завершена! На ваш Email отправлен код подтверждения.')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при регистрации: {e}')
            return self.form_invalid(form)

# --- Подтверждение регистрации ---
class UserVerifyRegistrationCodeView(FormView):
    """
    Представление для подтверждения регистрации с помощью одноразового кода.
    """
    template_name = 'users/verify_code.html'
    form_class = VerifyCodeForm
    success_url = '/users/login/' # После успешной регистрации перенаправляем на страницу входа.

    def get_initial(self):
        """
        Предоставляет начальные данные для формы.
        Извлекает email из сессии для скрытого поля.
        """
        initial = super().get_initial()
        initial['email'] = self.request.session.get('email_for_verification')
        return initial

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределение метода dispatch для проверки наличия email в сессии.
        Если email нет, перенаправляет пользователя на страницу регистрации.
        """
        if not self.request.session.get('email_for_verification'):
            messages.error(self.request, 'Отсутствует Email для верификации. Начните регистрацию заново.')
            return redirect('register')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Обработка данных, когда форма подтверждения кода валидна.
        Активирует пользователя и помечает код как использованный.
        """
        otp_code_obj = form.cleaned_data['otp_code_obj']
        user = otp_code_obj.user

        try:
            with transaction.atomic():
                # Активация пользователя.
                user.is_active = True
                user.save()
                # Пометка одноразового кода как использованного.
                otp_code_obj.is_used = True
                otp_code_obj.save()

                # Удаление email из сессии после успешной верификации.
                self.request.session.pop('email_for_verification', None)

            messages.success(self.request, 'Ваш аккаунт успешно подтвержден! Теперь вы можете войти.')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при подтверждении: {e}')
            return self.form_invalid(form)

# --- Запрос кода для входа ---
class UserLoginRequestCodeView(FormView):
    """
    Представление для запроса одноразового кода для входа.
    """
    template_name = 'users/login_request_code.html'
    form_class = UserLoginForm # Используем ту же форму, что и для регистрации, но с другой логикой
    success_url = '/users/verify-login-code/'

    def form_valid(self, form):
        """
        Обработка данных, когда форма запроса кода валидна.
        Генерирует новый одноразовый код для входа и сохраняет email в сессии.
        """
        user = form.cleaned_data['user_obj']
        try:
            with transaction.atomic():
                # Отключаем все неиспользованные и непросроченные коды для данного пользователя.
                OneTimeCode.objects.filter(user=user, is_used=False, expires_at__gt=timezone.now()).update(is_used=True)

                # Создание нового одноразового кода для входа.
                OneTimeCode.objects.create(
                    user=user,
                    type='login'
                )

                # Сохранение email в сессии для использования на следующем шаге.
                self.request.session['email_for_login_verification'] = user.email

            messages.success(self.request, 'Код для входа отправлен на ваш Email.')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при запросе кода: {e}')
            return self.form_invalid(form)

# --- Подтверждение входа ---
class UserLoginVerifyCodeView(FormView):
    """
    Представление для подтверждения входа с помощью одноразового кода.
    """
    template_name = 'users/verify_code.html'
    form_class = VerifyCodeForm
    success_url = '/home/' # Указываем URL домашней страницы или другую страницу после успешного входа.

    def get_initial(self):
        """
        Предоставляет начальные данные для формы.
        Извлекает email из сессии для скрытого поля.
        """
        initial = super().get_initial()
        initial['email'] = self.request.session.get('email_for_login_verification')
        return initial

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределение метода dispatch для проверки наличия email в сессии.
        Если email нет, перенаправляет пользователя на страницу запроса кода для входа.
        """
        if not self.request.session.get('email_for_login_verification'):
            messages.error(self.request, 'Отсутствует Email для входа. Запросите код для входа заново.')
            return redirect('login_request_code')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Если форма кода для входа валидна, входим пользователя в систему.
        """
        otp_code_obj = form.cleaned_data['otp_code_obj']
        user = otp_code_obj.user

        try:
            with transaction.atomic():
                # Помечаем код как использованный.
                otp_code_obj.is_used = True
                otp_code_obj.save()

                # Входим пользователя в систему.
                login(self.request, user)
                # Удаляем email из сессии.
                self.request.session.pop('email_for_login_verification', None)

            messages.success(self.request, 'Вы успешно вошли в систему!')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при входе: {e}')
            return self.form_invalid(form)

# --- Выход пользователя ---
class UserLogoutView(View):
    """
    Представление для выхода пользователя из системы.
    """
    def get(self, request, *args, **kwargs):
        """
        Обработка GET-запроса для выхода из системы.
        """
        logout(request)
        messages.info(request, 'Вы вышли из системы.')
        return redirect(reverse('login_request_code')) # Перенаправляем на страницу запроса кода для входа.