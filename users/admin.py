from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import OneTimeCode

# Получение текущей активной модели пользователя Django.
User = get_user_model()

@admin.register(OneTimeCode)
class OneTimeCodeAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели OneTimeCode в админ-панели.
    """
    list_display = ('user', 'code', 'type', 'created_at', 'expires_at', 'is_used', 'is_valid_display') # Поля, отображаемые в списке.
    list_filter = ('type', 'is_used', 'created_at') # Фильтры для списка.
    search_fields = ('user__email', 'code') # Поля для поиска.
    readonly_fields = ('created_at', 'expires_at') # Поля, доступные только для чтения.

    def is_valid_display(self, obj):
        """
        Отображает статус действительности кода.
        """
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Действителен'

try:
    # Попытка отмены регистрации стандартной модели User, если она уже зарегистрирована.
    # Это предотвращает ошибку AlreadyRegistered при повторной регистрации.
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    # Если модель еще не зарегистрирована, это нормально, просто пропускаем.
    pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Переопределение стандартных настроек отображения модели User в админ-панели.
    """
    list_display = ('email', 'username', 'is_staff', 'is_active', 'date_joined') # Поля, отображаемые в списке.
    search_fields = ('email', 'username') # Поля для поиска.
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (('Персональная информация'), {'fields': ('first_name', 'last_name')}),
        (('Разрешения'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password', 'password2'),
        }),
    )