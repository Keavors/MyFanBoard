from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import OneTimeCode

@receiver(post_save, sender=OneTimeCode)
def send_otp_email_on_create(sender, instance, created, **kwargs):
    """
    Отправляет одноразовый код по email, когда новый объект OneTimeCode сохраняется в базе данных.
    Этот сигнал срабатывает только при создании нового кода.
    """
    if created:
        subject = ''
        template_name = ''

        # Определение темы письма и шаблона в зависимости от типа кода.
        if instance.type == 'registration':
            subject = 'Подтверждение регистрации на фан-ресурсе MMORPG'
            template_name = 'emails/registration_otp_email.html'
        elif instance.type == 'login':
            subject = 'Код для входа на фан-ресурс MMORPG'
            template_name = 'emails/login_otp_email.html'
        elif instance.type == 'password_reset':
            subject = 'Сброс пароля на фан-ресурсе MMORPG'
            template_name = 'emails/password_reset_otp_email.html'
        else:
            # Если тип кода неизвестен, не отправляем письмо и выходим.
            print(f"Неизвестный тип OTP кода: {instance.type}. Email не будет отправлен.")
            return

        # Подготовка контекста для шаблона письма.
        context = {
            'username': instance.user.username if instance.user.username else instance.user.email,
            'otp_code': instance.code,
            'otp_type': instance.type,
        }

        # Рендеринг HTML-версии письма из шаблона.
        html_message = render_to_string(template_name, context)

        # Создание простой текстовой версии письма на случай, если HTML не поддерживается.
        plain_message = (
            f"Здравствуйте, {instance.user.username if instance.user.username else instance.user.email}!\n\n"
            f"Ваш {instance.type} код: {instance.code}.\n\n"
            f"Этот код действителен в течение 10 минут. Пожалуйста, не передавайте его никому.\n\n"
            f"Если вы не запрашивали этот код, просто проигнорируйте это письмо.\n\n"
            f"С уважением,\nКоманда фан-ресурса."
        )

        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            print(f"Отправлен {instance.type} код на {instance.user.email}")
        except Exception as e:
            print(f"Ошибка при отправке {instance.type} кода на {instance.user.email}: {e}")