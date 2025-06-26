from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import random
import string
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Получение текущей активной модели пользователя Django.
User = get_user_model()

class OneTimeCode(models.Model):
    """
    Модель для хранения одноразовых кодов (OTP) для подтверждения регистрации и входа.
    """
    CODE_TYPES = [
        ('registration', 'Подтверждение регистрации'),
        ('login', 'Вход в систему'),
        ('password_reset', 'Сброс пароля'), # Задел на будущее
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='one_time_codes',
        verbose_name='Пользователь'
    )
    code = models.CharField(
        max_length=6,
        unique=False,
        verbose_name='Код'
    )
    type = models.CharField(
        max_length=20,
        choices=CODE_TYPES,
        verbose_name='Тип кода'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    expires_at = models.DateTimeField(
        verbose_name='Срок действия'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='Использован'
    )

    class Meta:
        verbose_name = 'Одноразовый код'
        verbose_name_plural = 'Одноразовые коды'
        ordering = ['-created_at'] # Сортировка по дате создания (от новых к старым)

    def save(self, *args, **kwargs):
        """
        Переопределение метода сохранения для установки срока действия и генерации кода.
        """
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            # Код действует 10 минут.
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def generate_code(self):
        """
        Генерирует 6-значный цифровой код.
        """
        return ''.join(random.choices(string.digits, k=6))

    def is_valid(self):
        """
        Проверяет, действителен ли код (не использован и не просрочен).
        """
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        """
        Строковое представление объекта.
        """
        status = 'Использован' if self.is_used else 'Не использован'
        validity = 'Действителен' if self.is_valid() else 'Просрочен/Недействителен'
        return f"Код {self.code} ({self.type}) для {self.user.email} - {status}, {validity}"

class UserProfile(models.Model):
    """
    Модель профиля пользователя, расширяющая стандартную модель User.
    Содержит дополнительные поля для пользователя.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    is_subscribed_to_newsletter = models.BooleanField(
        default=True,
        verbose_name="Подписан на рассылку"
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return f"Профиль {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал, создающий или обновляющий профиль пользователя при сохранении объекта User.
    """
    if created:
        # Если пользователь только что создан, создаем для него профиль.
        UserProfile.objects.create(user=instance)
    else:
        # Если пользователь уже существует, пытаемся сохранить его профиль.
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            # Если профиля нет (например, если он был удален вручную), создаем его.
            UserProfile.objects.create(user=instance)