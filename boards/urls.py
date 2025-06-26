from django.urls import path
from . import views
from .views import UnsubscribeNewsletterView

app_name = 'boards'

urlpatterns = [
    # Список всех досок.
    path('', views.board_list, name='list'),
    # Посты по выбранной доске.
    path('<int:pk>/', views.posts_by_board, name='posts_by_board'),
    # Создание нового поста на доске.
    path('<int:pk>/new/', views.create_post, name='create_post'),
    # Детали конкретного поста.
    path('<int:board_pk>/post/<int:post_pk>/', views.post_detail, name='post_detail'),
    # Добавление отклика к посту.
    path('<int:board_pk>/post/<int:post_pk>/add_response/', views.add_response, name='add_response'),
    # Редактирование поста.
    path('<int:board_pk>/post/<int:post_pk>/edit/', views.edit_post, name='edit_post'),
    # Просмотр откликов на посты пользователя.
    path('my-posts-responses/', views.my_posts_responses_view, name='my_posts_responses'),
    # Принятие отклика.
    path('response/<int:pk>/accept/', views.accept_response_view, name='accept_response'),
    # Удаление отклика.
    path('response/<int:pk>/delete/', views.delete_response_view, name='delete_response'),
    # Отписка от новостной рассылки.
    path('unsubscribe/', UnsubscribeNewsletterView.as_view(), name='unsubscribe_newsletter'),
]