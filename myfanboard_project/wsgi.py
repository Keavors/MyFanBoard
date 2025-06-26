"""
Конфигурация WSGI для проекта myfanboard_project.

Этот файл предоставляет вызываемый объект WSGI в качестве переменной уровня модуля под названием ``application``.

Дополнительную информацию об этом файле см.:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myfanboard_project.settings')

application = get_wsgi_application()