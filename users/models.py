from django.db import models
from django.conf import settings # Используется для доступа к AUTH_USER_MODEL
from datetime import timedelta
from django.utils import timezone
import random
import string
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save # <-- Убедитесь, что этот импорт есть
from django.dispatch import receiver # <-- Убедитесь, что этот импорт есть

User = get_user_model() # Получаем модель User

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
        settings.AUTH_USER_MODEL, # Ссылка на стандартную модель пользователя Django
        on_delete=models.CASCADE, # Если пользователь удаляется, удаляются и его коды
        related_name='one_time_codes', # Для удобного доступа к кодам пользователя (user.one_time_codes.all())
        verbose_name='Пользователь'
    )
    code = models.CharField(
        max_length=6, # Например, 6-значный цифровой код
        unique=False, # Разрешаем несколько кодов для одного пользователя (но активный будет один)
        verbose_name='Код'
    )
    type = models.CharField(
        max_length=20,
        choices=CODE_TYPES, # Используем предопределенные типы кодов
        verbose_name='Тип кода'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, # Автоматически устанавливается при создании объекта
        verbose_name='Дата создания'
    )
    expires_at = models.DateTimeField( # Срок действия кода
        verbose_name='Срок действия'
    )
    is_used = models.BooleanField(
        default=False, # Флаг, указывающий, был ли код использован
        verbose_name='Использован'
    )

    class Meta:
        """
        Вложенный класс Meta используется для определения метаданных модели.
        """
        verbose_name = 'Одноразовый код' # Название модели в единственном числе для админки
        verbose_name_plural = 'Одноразовые коды' # Название модели во множественном числе для админки
        ordering = ['-created_at'] # Сортировка по убыванию даты создания (новые коды сверху)

    def __str__(self):
        """
        Метод для строкового представления объекта модели (удобно для админки).
        """
        return f"Код {self.code} для {self.user.email} ({self.type})"

    def is_valid(self):
        """
        Проверяет, является ли код действительным (не использован и не истек).
        """
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def generate_code(cls):
        """
        Статический метод для генерации 6-значного цифрового кода.
        """
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save() для автоматического задания expires_at
        при создании нового объекта.
        """
        if not self.id: # Проверяем, создается ли новый объект (у него еще нет ID)
            # Устанавливаем срок действия, например, 10 минут
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs) # Вызываем оригинальный метод save()

class UserProfile(models.Model): # Создаем отдельный профиль для дополнительных полей
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_subscribed_to_newsletter = models.BooleanField(default=True, verbose_name="Подписан на рассылку")

    def __str__(self):
        return f"Профиль {self.user.username}"

# --- ИСПРАВЛЕННЫЙ ОБРАБОТЧИК СИГНАЛА ---
# Объединяем создание и обновление профиля в одной функции.
# Эта функция будет вызываться каждый раз, когда объект User сохраняется.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Если пользователь только что создан, создаем для него профиль.
        # Это предотвратит ошибку, если профиль еще не существует.
        UserProfile.objects.create(user=instance)
    #else:
        # Если пользователь уже существует, пытаемся сохранить его профиль.
        # Используем try-except на случай, если профиль по каким-то причинам отсутствует
        # у УЖЕ СУЩЕСТВУЮЩЕГО пользователя (например, до добавления этой логики)
        # или был удален вручную.
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Если профиля нет (что теоретически не должно произойти для `existing` пользователя,
        # если `created=True` отработал корректно, но может быть, если его удалили),
        # можно создать его здесь.
        UserProfile.objects.create(user=instance)

# Удален дублирующийся сигнал save_user_profile
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#    instance.profile.save()
