from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Для настройки админки стандартной модели User
from django.contrib.auth import get_user_model # Получаем текущую модель User
from .models import OneTimeCode # Импортируем нашу модель

# Получаем модель пользователя Django
User = get_user_model()

# ---- Настройки для OneTimeCode в админке ----
@admin.register(OneTimeCode)
class OneTimeCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'type', 'created_at', 'expires_at', 'is_used', 'is_valid_display')
    list_filter = ('type', 'is_used', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at', 'expires_at')

    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Действителен'

# ---- Настройки для User в админке (Переопределение стандартного UserAdmin) ----

# Сначала отменяем регистрацию стандартной модели User, если она уже зарегистрирована
# Это важно, чтобы избежать ошибки AlreadyRegistered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass # Если модель еще не зарегистрирована, это нормально, просто пропускаем

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password', 'password2'),
        }),
    )