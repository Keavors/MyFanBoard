from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Response # Импортируем модель Response

# Здесь будут наши функции-ресиверы
@receiver(post_save, sender=Response)
def send_response_notification_email(sender, instance, created, **kwargs):
    """
    Отправляет email-уведомление автору поста, когда на его пост оставлен новый отклик.
    Срабатывает только при создании нового отклика.
    """
    if created: # Проверяем, что объект Response был только что создан (а не обновлен)
        response = instance
        post = response.post
        post_author = post.author
        response_author = response.author

        # Избегаем отправки уведомления самому себе, если автор ответа и автор поста совпадают
        if response_author == post_author:
            return

        subject = f'Новый отклик на ваш пост "{post.title[:50]}..."'
        template_name = 'emails/new_response_email.html'

        # Формируем полный URL к посту
        # request=None, потому что мы находимся вне контекста запроса.
        # Это сработает, если SITE_URL в settings.py настроен корректно.
        # Или можно использовать RequestSite, но для простоты пока оставим так.
        # Если будет ошибка "NoReverseMatch" или некорректный URL,
        # нужно будет настроить домен сайта в settings.py или использовать более сложный подход.
        post_url = settings.SITE_URL + reverse('boards:post_detail', args=[post.board.pk, post.pk])

        context = {
            'post_author_username': post_author.username,
            'post_author_email': post_author.email,
            'post_title': post.title,
            'response_author_username': response_author.username,
            'response_author_email': response_author.email,
            'response_content': response.content,
            'post_url': post_url,
        }

        # Рендерим HTML-версию письма
        html_message = render_to_string(template_name, context)

        # Создаем простую текстовую версию письма
        plain_message = (
            f"Здравствуйте, {post_author.username if post_author.username else post_author.email}!\n\n"
            f"На ваш пост \"{post.title}\" был оставлен новый отклик.\n\n"
            f"Автор отклика: {response_author.username if response_author.username else response_author.email}\n"
            f"Содержание отклика: {response.content}\n\n"
            f"Перейти к посту: {post_url}\n\n"
            f"С уважением,\nКоманда фан-ресурса."
        )

        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [post_author.email],
                html_message=html_message,
                fail_silently=False,
            )
            print(f"DEBUG: Отправлено уведомление о новом отклике на пост '{post.title}' автору {post_author.email}")
        except Exception as e:
            print(f"ERROR: Не удалось отправить уведомление о новом отклике на пост '{post.title}' автору {post_author.email}: {e}")
