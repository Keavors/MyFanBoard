from django.urls import path
from . import views # Импортируем представления из текущей папки

urlpatterns = [
    path('', views.home, name='home'), # Главная страница
]