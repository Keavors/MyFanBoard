"""
Конфигурация URL для проекта myfanboard_project.

Список `urlpatterns` направляет URL-адреса к представлениям. Дополнительную информацию см.:
https://docs.djangoproject.com/en/5.2/topics/http/urls/

Примеры:
Функциональные представления
    1. Добавьте импорт: from my_app import views
    2. Добавьте URL в urlpatterns: path('', views.home, name='home')
Представления на основе классов
    1. Добавьте импорт: from other_app.views import Home
    2. Добавьте URL в urlpatterns: path('', Home.as_view(), name='home')
Включение другого URLconf
    1. Импортируйте функцию include(): from django.urls import include, path
    2. Добавьте URL в urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('main.urls')),
    path("boards/", include('boards.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

# Для обслуживания медиафайлов и статических файлов в режиме разработки (НЕ ДЛЯ PRODUCTION!)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)