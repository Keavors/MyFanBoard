from django.apps import AppConfig


class BoardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boards'
    verbose_name = 'Доски объявлений' # Добавим человекочитаемое имя для админки

    def ready(self):
        """
        Метод, который вызывается при старте приложения Django.
        Здесь мы импортируем наши сигналы, чтобы они были зарегистрированы.
        """
        import boards.signals