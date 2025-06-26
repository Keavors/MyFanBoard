"""
Конфигурация ASGI для проекта myfanboard_project.

Этот файл предоставляет вызываемый объект ASGI в качестве переменной уровня модуля под названием ``application``.

Дополнительную информацию об этом файле см.:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myfanboard_project.settings')

application = get_asgi_application()