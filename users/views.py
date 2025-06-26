from django.shortcuts import render, redirect, reverse # Функции для рендеринга шаблонов, перенаправления
from django.utils import timezone
from django.views.generic import View, FormView # Базовые классы для представлений
from django.contrib.auth import login, logout, authenticate # Функции для входа/выхода/аутентификации пользователя
from django.contrib import messages # Для вывода сообщений пользователю
from django.contrib.auth import get_user_model # Получаем модель пользователя Django
from django.db import transaction # Для работы с транзакциями базы данных

from .forms import UserRegisterForm, VerifyCodeForm, UserLoginForm # Наши формы
from .models import OneTimeCode # Наша модель OneTimeCode

User = get_user_model() # Получаем модель User

# --- Регистрация пользователя ---
class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/users/verify-registration-code/'

    def form_valid(self, form):
        """
        Этот метод вызывается, если форма прошла валидацию.
        Создаем пользователя и OneTimeCode, затем перенаправляем на страницу подтверждения.
        """
        email = form.cleaned_data['email']
        try:
            with transaction.atomic():
                # Создаем нового пользователя (неактивного по умолчанию)
                user = User.objects.create_user(email=email, username=email.split('@')[0])
                user.is_active = False # Пользователь неактивен до подтверждения
                user.save()

                # Создаем OneTimeCode для регистрации.
                # Сигнал post_save для OneTimeCode отправит письмо.
                OneTimeCode.objects.create(
                    user=user,
                    code=OneTimeCode.generate_code(),
                    type='registration'
                )

            self.request.session['email_for_verification'] = email
            messages.success(self.request, 'На ваш Email отправлен код подтверждения. Проверьте почту.')
            return super().form_valid(form)

        except Exception as e:
            print(f"DEBUG: Ошибка при регистрации: {e}") # Для отладки
            messages.error(self.request, f'Произошла ошибка при регистрации: {e}')
            return self.form_invalid(form)

class UserVerifyRegistrationCodeView(FormView):
    template_name = 'users/verify_code.html' # Шаблон для ввода кода
    form_class = VerifyCodeForm # Используем нашу форму VerifyCodeForm
    success_url = '/' # Куда перенаправить после успешного подтверждения (например, на главную)

    def get_initial(self):
        """
        Получаем начальные данные для формы (в данном случае, email из сессии).
        """
        initial = super().get_initial()
        initial['email'] = self.request.session.get('email_for_verification')
        return initial

    def get_context_data(self, **kwargs):
        """
        Добавляем email в контекст шаблона, чтобы его можно было отобразить.
        """
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('email_for_verification')
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяем, есть ли email в сессии, прежде чем показывать форму.
        Если нет, перенаправляем на страницу регистрации.
        """
        if not self.request.session.get('email_for_verification'):
            messages.error(self.request, 'Отсутствует Email для верификации. Начните регистрацию заново.')
            return redirect('register') # 'register' - это имя URL-адреса для регистрации
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print("DEBUG VIEW: UserVerifyRegistrationCodeView.form_valid() вызван.") # <-- Добавлено

        otp_code_obj = form.cleaned_data.get('otp_code_obj') # Используем .get() для безопасности
        if not otp_code_obj:
            # Этого не должно произойти, если form.clean() работает правильно,
            # но на всякий случай для дополнительной отладки.
            print("DEBUG VIEW: otp_code_obj не найден в cleaned_data после form_valid.") # <-- Добавлено
            messages.error(self.request, 'Ошибка валидации формы: код не найден.')
            return self.form_invalid(form)


        user = otp_code_obj.user
        print(f"DEBUG VIEW: Пользователь из кода: {user.email}, Активен: {user.is_active}") # <-- Добавлено

        try:
            with transaction.atomic():
                user.is_active = True
                user.save()
                print(f"DEBUG VIEW: Пользователь {user.email} активирован.") # <-- Добавлено

                otp_code_obj.is_used = True
                otp_code_obj.save()
                print(f"DEBUG VIEW: Код {otp_code_obj.code} помечен как использованный.") # <-- Добавлено

                login(self.request, user) # <-- Вернули логин
                print(f"DEBUG VIEW: Пользователь {user.email} вошел в систему.") # <-- Добавлено

                self.request.session.pop('email_for_verification', None) # Удаляем безопасно
                print("DEBUG VIEW: email_for_verification удален из сессии.") # <-- Добавлено

            messages.success(self.request, 'Ваша регистрация успешно подтверждена. Вы вошли в систему!')
            print("DEBUG VIEW: form_valid() успешно завершен.") # <-- Добавлено
            return super().form_valid(form)

        except Exception as e:
            # Более явный вывод ошибки из views.py
            import traceback
            traceback.print_exc() # Выводим полный traceback в консоль
            print(f"DEBUG VIEW: ОБЩАЯ ОШИБКА В form_valid: {e}")
            messages.error(self.request, f'Произошла ошибка при подтверждении: {e}')
            return self.form_invalid(form)

# --- Вход пользователя ---
class UserLoginRequestCodeView(FormView):
    template_name = 'users/login_request_code.html' # Шаблон для запроса кода входа
    form_class = UserLoginForm # Используем форму для запроса email при входе
    success_url = '/users/verify-login-code/' # Куда перенаправить после запроса кода

    def form_valid(self, form):
        """
        Если форма запроса email для входа валидна, генерируем OTP и отправляем email.
        """
        user = form.cleaned_data['user_obj']
        email = form.cleaned_data['email']

        try:
            with transaction.atomic():
                # Перед созданием нового, деактивируем все старые неиспользованные коды 'login' для этого пользователя
                # Это предотвратит использование старых просроченных кодов
                OneTimeCode.objects.filter(
                    user=user,
                    type='login',
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).update(is_used=True) # Помечаем старые как использованные

                # Генерируем новый код для входа
                OneTimeCode.objects.create(
                    user=user,
                    code=OneTimeCode.generate_code(),
                    type='login'
                )
            self.request.session['email_for_login_verification'] = email # Сохраняем email в сессии
            messages.success(self.request, 'Код для входа отправлен на ваш Email. Проверьте почту.')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при отправке кода: {e}')
            return self.form_invalid(form)

class UserLoginVerifyCodeView(FormView):
    template_name = 'users/verify_code.html' # Используем тот же шаблон для ввода кода
    form_class = VerifyCodeForm # Используем ту же форму VerifyCodeForm
    success_url = '/' # Куда перенаправить после успешного входа

    def get_initial(self):
        """
        Получаем начальные данные для формы (email из сессии для входа).
        """
        initial = super().get_initial()
        initial['email'] = self.request.session.get('email_for_login_verification')
        return initial

    def get_context_data(self, **kwargs):
        """
        Добавляем email в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('email_for_login_verification')
        context['is_login_flow'] = True # Флаг для шаблона, если нужно что-то менять для входа
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяем, есть ли email в сессии, прежде чем показывать форму.
        """
        if not self.request.session.get('email_for_login_verification'):
            messages.error(self.request, 'Отсутствует Email для входа. Запросите код для входа заново.')
            return redirect('login_request_code') # 'login_request_code' - имя URL-адреса

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Если форма кода для входа валидна, входим пользователя в систему.
        """
        otp_code_obj = form.cleaned_data['otp_code_obj']
        user = otp_code_obj.user

        try:
            with transaction.atomic():
                otp_code_obj.is_used = True # Помечаем код как использованный
                otp_code_obj.save()

                login(self.request, user) # Входим пользователя в систему
                self.request.session.pop('email_for_login_verification', None) # Удаляем безопасно

            messages.success(self.request, 'Вы успешно вошли в систему!')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при входе: {e}')
            return self.form_invalid(form)

# --- Выход пользователя ---
class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request) # Функция выхода из Django
        messages.info(request, 'Вы вышли из системы.')
        return redirect('/') # Перенаправляем на главную страницу