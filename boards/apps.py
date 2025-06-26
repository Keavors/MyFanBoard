from django.apps import AppConfig


class BoardsConfig(AppConfig):
    """
    Конфигурация приложения "Доски объявлений".
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boards'
    verbose_name = 'Доски объявлений'

    def ready(self):
        """
        Метод, вызываемый при старте приложения Django.
        Импортирует и регистрирует обработчики сигналов.
        """
        import boards.signals