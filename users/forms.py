from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model # Получаем текущую активную модель пользователя Django
from django.core.exceptions import ValidationError # Для вызова ошибок валидации
from .models import OneTimeCode # Импортируем нашу модель OneTimeCode

User = get_user_model() # Получаем модель User, которую использует Django (по умолчанию django.contrib.auth.models.User)

class UserRegisterForm(forms.Form):
    """
    Форма для регистрации нового пользователя.
    Требует только email.
    """
    email = forms.EmailField(
        label='Ваш Email',
        max_length=254,
        help_text='На этот адрес будет отправлен код подтверждения.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )

    def clean_email(self):
        """
        Метод валидации для поля email.
        Проверяет, что пользователь с таким email еще не зарегистрирован.
        """
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

class VerifyCodeForm(forms.Form):
    """
    Форма для ввода одноразового кода.
    """
    code = forms.CharField(
        label='Код подтверждения',
        max_length=6,
        min_length=6,
        help_text='Введите 6-значный код, полученный на ваш Email.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите код'})
    )

    # Это поле будет хранить email, для которого проверяется код.
    # Оно будет невидимым для пользователя (hidden field), но обязательным для передачи.
    email = forms.EmailField(widget=forms.HiddenInput())


    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        email = cleaned_data.get('email')
        print(f"DEBUG FORM: clean() - Code: {code}, Email: {email}") # <-- Добавлено

        if not code or not email:
            return cleaned_data

        try:
            otp_code = OneTimeCode.objects.filter(
                user__email=email,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).order_by('-created_at').first()

            if not otp_code:
                print("DEBUG FORM: clean() - Код не найден или просрочен.") # <-- Добавлено
                raise ValidationError('Неверный или просроченный код. Пожалуйста, попробуйте снова или запросите новый.')

            cleaned_data['otp_code_obj'] = otp_code
            print(f"DEBUG FORM: clean() - Код найден и действителен для пользователя: {otp_code.user.email}") # <-- Добавлено

        except OneTimeCode.DoesNotExist:
            print("DEBUG FORM: clean() - OneTimeCode.DoesNotExist.") # <-- Добавлено
            raise ValidationError('Неверный или просроченный код. Пожалуйста, попробуйте снова или запросите новый.')
        except Exception as e:
            print(f"DEBUG FORM: Общая ошибка при валидации VerifyCodeForm: {e}") # <-- Добавлено
            raise ValidationError('Произошла ошибка. Пожалуйста, попробуйте позже.')

        return cleaned_data

class UserLoginForm(forms.Form):
    """
    Форма для запроса кода для входа. Требует только email.
    """
    email = forms.EmailField(
        label='Ваш Email',
        max_length=254,
        help_text='На этот адрес будет отправлен код для входа.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )

    def clean_email(self):
        """
        Метод валидации для поля email при входе.
        Проверяет, что пользователь с таким email существует и активен.
        """
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            # Сохраняем пользователя в cleaned_data, чтобы его можно было использовать во views
            self.cleaned_data['user_obj'] = user
        except User.DoesNotExist:
            raise ValidationError('Пользователь с таким email не найден или не активен.')
        return email