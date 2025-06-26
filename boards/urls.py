from django.urls import path
from . import views
from .views import UnsubscribeNewsletterView

app_name = 'boards'

urlpatterns = [
    path('', views.board_list, name='list'),
    path('<int:pk>/', views.posts_by_board, name='posts_by_board'),
    path('<int:pk>/new/', views.create_post, name='create_post'),
    path('<int:board_pk>/post/<int:post_pk>/', views.post_detail, name='post_detail'),
    path('<int:board_pk>/post/<int:post_pk>/add_response/', views.add_response, name='add_response'),
    path('<int:board_pk>/post/<int:post_pk>/edit/', views.edit_post, name='edit_post'),
    path('my-posts-responses/', views.my_posts_responses_view, name='my_posts_responses'),
    path('response/<int:pk>/accept/', views.accept_response_view, name='accept_response'),
    path('response/<int:pk>/delete/', views.delete_response_view, name='delete_response'),
    path('unsubscribe/', UnsubscribeNewsletterView.as_view(), name='unsubscribe_newsletter'),
]