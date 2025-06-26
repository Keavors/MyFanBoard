from django.apps import AppConfig

class UsersConfig(AppConfig):
    """
    Конфигурация приложения "Пользователи".
    """
    # Автоматическое создание первичного ключа.
    default_auto_field = 'django.db.models.BigAutoField'
    # Имя приложения.
    name = 'users'
    # Человекочитаемое имя для админ-панели.
    verbose_name = 'Пользователи'

    def ready(self):
        """
        Метод, вызываемый при запуске приложения Django.
        Здесь происходит импорт сигналов для их регистрации.
        """
        import users.signals