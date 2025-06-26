# users/signals.py
from django.db.models.signals import post_save # Сигнал, который отправляется после сохранения объекта
from django.dispatch import receiver         # Декоратор для регистрации функций-ресиверов
from django.core.mail import send_mail       # Функция для отправки email
from django.template.loader import render_to_string # Для рендеринга HTML-шаблонов писем
from django.conf import settings             # Для доступа к настройкам проекта (например, DEFAULT_FROM_EMAIL)
from .models import OneTimeCode              # Импортируем нашу модель OneTimeCode

@receiver(post_save, sender=OneTimeCode)
def send_otp_email_on_create(sender, instance, created, **kwargs):
    """
    Отправляет одноразовый код по email, когда новый объект OneTimeCode сохраняется в базе данных.
    Этот сигнал срабатывает только при создании нового кода.
    """
    if created: # Проверяем, что объект OneTimeCode был только что создан (а не обновлен)
        subject = ''
        template_name = ''

        # Определяем тему письма и шаблон в зависимости от типа кода
        if instance.type == 'registration':
            subject = 'Подтверждение регистрации на фан-ресурсе MMORPG'
            template_name = 'emails/registration_otp_email.html' # <-- ИЗМЕНЕНО
        elif instance.type == 'login':
            subject = 'Код для входа на фан-ресурс MMORPG'
            template_name = 'emails/login_otp_email.html' # <-- ИЗМЕНЕНО
        elif instance.type == 'password_reset':
            subject = 'Код для сброса пароля на фан-ресурсе MMORPG'
            template_name = 'emails/password_reset_otp_email.html' # <-- ИЗМЕНЕНО

        context = {
            'user': instance.user,    # Пользователь, которому отправляется код
            'code': instance.code,  # Сам одноразовый код
            'otp_type': instance.type, # Тип кода (для возможного использования в шаблоне)
        }

        # Рендерим HTML-версию письма из шаблона
        html_message = render_to_string(template_name, context)
        # Создаем простую текстовую версию письма на случай, если HTML не поддерживается
        plain_message = (
            f"Здравствуйте, {instance.user.username if instance.user.username else instance.user.email}!\\n\\n"
            f"Ваш {instance.type} код: {instance.code}.\\n\\n"
            f"Этот код действителен в течение 10 минут. Пожалуйста, не передавайте его никому.\\n\\n"
            f"Если вы не запрашивали этот код, просто проигнорируйте это письмо.\\n\\n"
            f"С уважением,\\nКоманда фан-ресурса."
        )

        try:
            send_mail(
                subject,                 # Тема письма
                plain_message,           # Текстовая версия письма
                settings.DEFAULT_FROM_EMAIL, # От кого письмо (настраивается в settings.py)
                [instance.user.email],   # Кому письмо
                html_message=html_message, # HTML-версия письма
                fail_silently=False,     # Если True, ошибки отправки не вызывают исключений
            )
            print(f"Отправлен {instance.type} OTP для {instance.user.email}")
        except Exception as e:
            print(f"Ошибка при отправке {instance.type} OTP для {instance.user.email}: {e}")