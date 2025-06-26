from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import OneTimeCode

# Получение текущей активной модели пользователя Django.
User = get_user_model()

class UserRegisterForm(forms.Form):
    """
    Форма для регистрации нового пользователя.
    Требует только Email.
    """
    email = forms.EmailField(
        label='Ваш Email',
        max_length=254,
        help_text='На этот адрес будет отправлен код подтверждения.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )

    def clean_email(self):
        """
        Метод валидации для поля Email.
        Проверяет, что пользователь с таким Email еще не зарегистрирован.
        """
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким Email уже зарегистрирован.')
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

    # Это поле будет хранить Email, для которого проверяется код.
    # Оно невидимо для пользователя (скрытое поле), но обязательно для передачи.
    email = forms.EmailField(widget=forms.HiddenInput())


    def clean(self):
        """
        Метод общей валидации формы.
        Проверяет наличие и срок действия одноразового кода.
        """
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        email = cleaned_data.get('email')

        if not code or not email:
            return cleaned_data

        try:
            # Поиск одноразового кода, соответствующего Email, коду, неиспользованного и непросроченного.
            otp_code = OneTimeCode.objects.filter(
                user__email=email,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).order_by('-created_at').first()

            if not otp_code:
                raise ValidationError('Неверный или просроченный код. Пожалуйста, попробуйте снова или запросите новый.')

            cleaned_data['otp_code_obj'] = otp_code

        except OneTimeCode.DoesNotExist:
            raise ValidationError('Неверный или просроченный код. Пожалуйста, попробуйте снова или запросите новый.')
        except Exception as e:
            raise ValidationError('Произошла ошибка. Пожалуйста, попробуйте позже.')

        return cleaned_data

class UserLoginForm(forms.Form):
    """
    Форма для запроса кода для входа. Требует только Email.
    """
    email = forms.EmailField(
        label='Ваш Email',
        max_length=254,
        help_text='На этот адрес будет отправлен код для входа.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )

    def clean_email(self):
        """
        Метод валидации для поля Email при входе.
        Проверяет, что пользователь с таким Email существует и активен.
        """
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            # Сохранение пользователя в cleaned_data для дальнейшего использования в представлениях.
            self.cleaned_data['user_obj'] = user
        except User.DoesNotExist:
            raise ValidationError('Пользователь с таким Email не найден или не активен.')
        return email