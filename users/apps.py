# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи' # Добавим человекочитаемое имя для админки

    def ready(self):
        """
        Метод, который вызывается при старте приложения Django.
        Здесь мы импортируем наши сигналы, чтобы они были зарегистрированы.
        """
        import users.signals