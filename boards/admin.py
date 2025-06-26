from django.contrib import admin
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

from django.contrib.auth import get_user_model # <-- ИСПРАВЛЕНО: Импорт User модели

from .models import Board, Post, Response, Newsletter # Добавьте Newsletter

# ИСПРАВЛЕНО: Получаем модель пользователя
User = get_user_model()

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'author', 'created_at', 'views')
    list_filter = ('board', 'author', 'created_at')
    search_fields = ('title', 'content')
    raw_id_fields = ('author', 'board')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at', 'is_accepted')
    list_filter = ('is_accepted', 'created_at', 'post__board', 'author')
    search_fields = ('content', 'post__title', 'author__username')
    raw_id_fields = ('post', 'author')
    actions = ['mark_as_accepted', 'mark_as_unaccepted']

    @admin.action(description='Пометить выбранные отклики как принятые')
    def mark_as_accepted(self, request, queryset):
        queryset.update(is_accepted=True)
        self.message_user(request, "Выбранные отклики успешно помечены как принятые.")

    @admin.action(description='Пометить выбранные отклики как непринятые')
    def mark_as_unaccepted(self, request, queryset):
        queryset.update(is_accepted=False)
        self.message_user(request, "Выбранные отклики успешно помечены как непринятые.")

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'sent_at', 'is_sent')
    list_filter = ('is_sent', 'created_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('created_at', 'sent_at', 'is_sent')

    actions = ['send_newsletter']

    @admin.action(description='Отправить выбранные рассылки')
    def send_newsletter(self, request, queryset):
        # ИСПРАВЛЕНО: Теперь 'User' будет распознаваться.
        # Выберите ОДИН из этих вариантов для определения получателей рассылки:
        #
        # Вариант 1: Отправлять всем активным пользователям (как было изначально)
        users_to_receive_newsletter = User.objects.filter(is_active=True)
        #
        # Вариант 2: Отправлять только активным пользователям, которые подписаны (если у вас есть такое поле в модели User)
        # users_to_receive_newsletter = User.objects.filter(is_active=True, is_subscribed_to_newsletter=True)
        #
        # Вариант 3: Отправлять только активным пользователям, у которых профиль подписан (если у вас есть модель Profile)
        # users_to_receive_newsletter = User.objects.filter(is_active=True, profile__is_subscribed_to_newsletter=True)


        emails_sent_count = 0
        emails_failed_count = 0

        for newsletter in queryset:
            if not newsletter.is_sent:
                subject = newsletter.subject
                template_name = 'boards/emails/newsletter_email.html' # Путь к вашему шаблону письма

                for user in users_to_receive_newsletter:
                    unsubscribe_url = '#' # Пока заглушка для ссылки отписки

                    context = {
                        'subject': subject,
                        'newsletter_content': newsletter.content,
                        'recipient_username': user.username if user.username else user.email,
                        'unsubscribe_url': unsubscribe_url,
                        'current_year': timezone.now().year,
                    }

                    plain_message = f"Здравствуйте, {context['recipient_username']}!\n\n{newsletter.content}\n\nС уважением,\nКоманда MyFanBoard."
                    html_message = render_to_string(template_name, context)

                    try:
                        send_mail(
                            subject,
                            plain_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        emails_sent_count += 1
                    except Exception as e:
                        emails_failed_count += 1
                        print(f"Ошибка при отправке рассылки пользователю {user.email}: {e}")

                if emails_sent_count > 0:
                    newsletter.is_sent = True
                    newsletter.sent_at = timezone.now()
                    newsletter.save()
                    self.message_user(request, f'Рассылка "{newsletter.subject}" успешно отправлена {emails_sent_count} пользователям.', level='success')
                    if emails_failed_count > 0:
                        self.message_user(request, f'{emails_failed_count} писем не удалось отправить.', level='error')
                else:
                    self.message_user(request, f'Рассылка "{newsletter.subject}" не была отправлена ни одному пользователю (возможно, нет активных пользователей или произошла ошибка).', level='warning')
            else:
                self.message_user(request, f'Рассылка "{newsletter.subject}" уже была отправлена ранее.', level='info')

        self.message_user(request, f'Завершено действие отправки рассылок.', level='info')