# MyFanBoard/boards/models.py

from django.db import models
from django.contrib.auth import get_user_model # Для связи с моделью пользователя
from django.utils import timezone # Для отметки времени
from django_ckeditor_5.fields import CKEditor5Field

# Получаем текущую активную модель пользователя
User = get_user_model()

class Board(models.Model):
    """
    Модель для представления доски объявлений (категории, форума).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название доски")
    description = models.TextField(blank=True, verbose_name="Описание доски")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"
        ordering = ['name'] # Сортировка по названию по умолчанию

    def __str__(self):
        return self.name

class Post(models.Model):
    """
    Модель для представления поста (темы) на доске.
    """
    title = models.CharField(max_length=200, verbose_name="Заголовок поста")
    content = CKEditor5Field(verbose_name="Содержимое поста", config_name='default') # Используем 'default' для простоты, как в настройках
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='posts', verbose_name="Доска")
    # Поле для хранения количества просмотров, если это нужно
    views = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров") # Переименовал views_count в views для консистентности

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at'] # Сортировка по дате создания (новые сверху)

    def __str__(self):
        return self.title[:50] + ('...' if len(self.title) > 50 else '') # Возвращаем первые 50 символов заголовка

class Response(models.Model):
    """
    Модель для откликов на объявления (посты).
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses', verbose_name="Объявление")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses', verbose_name="Автор отклика")
    content = CKEditor5Field(verbose_name="Текст отклика", config_name='default') # <-- ИЗМЕНЕНО: text на content, и тип на CKEditor5Field
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_accepted = models.BooleanField(default=False, verbose_name="Принят ли отклик")
    # Добавил updated_at для консистентности, хотя в вашем original Response его не было. Если не нужно - удалите.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ['created_at'] # Сортировка по дате создания (старые сверху)

    def __str__(self):
        return f"Отклик от {self.author.username} на '{self.post.title[:30]}...'"

class Newsletter(models.Model):
    """
    Модель для новостных рассылок.
    """
    subject = models.CharField(max_length=255, verbose_name="Тема рассылки")
    content = CKEditor5Field(verbose_name="Содержание рассылки", config_name='default')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата отправки")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлено?")

    class Meta:
        verbose_name = "Новостная рассылка"
        verbose_name_plural = "Новостные рассылки"
        ordering = ['-created_at']

    def __str__(self):
        return self.subject