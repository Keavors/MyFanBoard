from django.urls import path
from . import views

urlpatterns = [
    # Главная страница.
    path('', views.home, name='home'),
]