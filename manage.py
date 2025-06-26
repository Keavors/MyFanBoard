#!/usr/bin/env python
"""
Утилита командной строки Django для выполнения административных задач.
"""
import os
import sys


def main():
    """
    Запускает административные задачи Django.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myfanboard_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что он установлен и "
            "доступен в переменной окружения PYTHONPATH. Вы забыли "
            "активировать виртуальное окружение?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()