from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F
from django.contrib import messages # Для вывода сообщений пользователю
from django.http import Http404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Board, Post, Response
from .forms import PostForm, ResponseForm
from django.urls import reverse_lazy # Для использования в success_url, если будете делать FormView для отписки
from django.contrib.auth.mixins import LoginRequiredMixin # Для защиты представления
from django.views import View # Базовый класс для представлений

# --- Представления для досок ---
def board_list(request):
    boards = Board.objects.all()
    return render(request, 'boards/board_list.html', {'boards': boards})

def posts_by_board(request, pk):
    board = get_object_or_404(Board, pk=pk)
    posts = Post.objects.filter(board=board).order_by('-created_at')
    return render(request, 'boards/posts_by_board.html', {'board': board, 'posts': posts})

# --- Представления для постов ---
@login_required
def create_post(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.board = board
            post.author = request.user
            post.save()
            messages.success(request, 'Ваш пост успешно создан!') # Добавляем сообщение
            return redirect('boards:post_detail', board_pk=board.pk, post_pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'boards/post_create.html', {'form': form, 'board': board})

def post_detail(request, board_pk, post_pk):
    post = get_object_or_404(Post, board__pk=board_pk, pk=post_pk)

    # Увеличиваем счетчик просмотров
    Post.objects.filter(pk=post_pk).update(views=F('views') + 1)
    post.refresh_from_db() # Обновляем объект, чтобы получить актуальное значение views

    responses = Response.objects.filter(post=post).order_by('created_at')
    form = ResponseForm() # Создаем пустую форму для ответа

    return render(request, 'boards/post_detail.html', {
        'post': post,
        'responses': responses,
        'form': form
    })

@login_required
def add_response(request, board_pk, post_pk):
    post = get_object_or_404(Post, board__pk=board_pk, pk=post_pk)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.post = post
            response.author = request.user
            response.save()
            messages.success(request, 'Ваш ответ успешно добавлен!') # Добавляем сообщение
            return redirect(reverse('boards:post_detail', args=[board_pk, post_pk]) + '#responses')
    else: # Если был GET-запрос на add_response, просто перенаправляем на post_detail
        return redirect('boards:post_detail', board_pk=board_pk, post_pk=post_pk)

    # Этот return render будет только если POST-запрос был невалидным,
    # что не должно происходить при перенаправлении.
    return render(request, 'boards/post_detail.html', {'form': form, 'post': post})


@login_required
def edit_post(request, board_pk, post_pk):
    post = get_object_or_404(Post, board__pk=board_pk, pk=post_pk)

    # Проверяем, что текущий пользователь является автором поста
    if request.user != post.author:
        messages.error(request, 'У вас нет прав для редактирования этого поста.')
        return redirect('boards:post_detail', board_pk=board_pk, post_pk=post_pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post) # Загружаем данные в существующий объект
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('boards:post_detail', board_pk=board_pk, post_pk=post_pk)
    else:
        form = PostForm(instance=post) # Инициализируем форму существующими данными поста

    return render(request, 'boards/post_edit.html', {'form': form, 'post': post, 'board': post.board})

@login_required
def my_posts_responses_view(request):
    """
    Отображает отклики на объявления, созданные текущим пользователем.
    Также позволяет фильтровать отклики по конкретным объявлениям.
    """
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    selected_post_id = request.GET.get('post') # Получаем ID поста из GET-параметра

    responses = Response.objects.filter(post__author=request.user).order_by('-created_at')

    if selected_post_id:
        try:
            # Проверяем, что выбранный пост действительно принадлежит текущему пользователю
            selected_post = user_posts.get(pk=selected_post_id)
            responses = responses.filter(post=selected_post)
            messages.info(request, f'Отклики отфильтрованы по посту: "{selected_post.title}"')
        except Post.DoesNotExist:
            messages.error(request, 'Выбранный пост не существует или не принадлежит вам.')
            selected_post_id = None # Сбрасываем, чтобы показать все отклики
            responses = Response.objects.filter(post__author=request.user).order_by('-created_at') # И снова получаем все

    context = {
        'user_posts': user_posts,
        'responses': responses,
        'selected_post_id': selected_post_id,
        'has_responses': responses.exists(),
    }
    return render(request, 'boards/my_posts_responses.html', context)


@login_required
def accept_response_view(request, pk):
    """
    Представление для принятия отклика.
    Только автор поста может принять отклик на свой пост.
    Отправляет уведомление автору отклика.
    """
    response = get_object_or_404(Response, pk=pk)

    # Проверяем, является ли текущий пользователь автором поста,
    # к которому относится этот отклик
    if request.user != response.post.author:
        messages.error(request, 'У вас нет прав для принятия этого отклика.')
        return redirect('boards:my_posts_responses')

    if request.method == 'POST':
        if response.is_accepted:
            messages.info(request, 'Отклик уже был принят.')
        else:
            response.is_accepted = True
            response.save()
            messages.success(request, 'Отклик успешно принят!')

            # --- Отправка уведомления автору отклика ---
            subject = f'Ваш отклик на пост "{response.post.title}" был принят!'
            template_name = 'emails/response_accepted_email.html'
            context = {
                'recipient_username': response.author.username,
                'post_title': response.post.title,
                'post_url': request.build_absolute_uri(reverse('boards:post_detail', args=[response.post.board.pk, response.post.pk])),
                'response_content': response.content,
            }

            html_message = render_to_string(template_name, context)
            plain_message = (
                f"Здравствуйте, {response.author.username}!\n\n"
                f"Ваш отклик на пост \"{response.post.title}\" был принят автором.\n\n"
                f"Содержание вашего отклика: {response.content}\n\n"
                f"Вы можете посмотреть пост здесь: {context['post_url']}\n\n"
                f"С уважением,\nКоманда MyFanBoard."
            )
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [response.author.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.info(request, f'Уведомление отправлено автору отклика ({response.author.email}).')
            except Exception as e:
                messages.error(request, f'Не удалось отправить уведомление автору отклика: {e}')
            # --- Конец отправки уведомления ---

    return redirect('boards:my_posts_responses')


@login_required
def delete_response_view(request, pk):
    """
    Представление для удаления отклика.
    Только автор отклика или автор поста могут удалить отклик.
    В данном контексте "отклики на мои объявления" - удалять должен автор поста.
    """
    response = get_object_or_404(Response, pk=pk)

    # В контексте "откликов на мои объявления" удалять может только автор поста.
    # Если вы хотите, чтобы автор отклика тоже мог удалять свои отклики с этой страницы,
    # то нужно добавить `request.user == response.author`
    if request.user != response.post.author:
        messages.error(request, 'У вас нет прав для удаления этого отклика.')
        return redirect('boards:my_posts_responses')

    if request.method == 'POST':
        response.delete()
        messages.success(request, 'Отклик успешно удален!')
        return redirect('boards:my_posts_responses')
    else:
        messages.info(request, 'Используйте метод POST для удаления отклика.')
        return redirect('boards:my_posts_responses')

class UnsubscribeNewsletterView(LoginRequiredMixin, View):
    """
    Представление для отписки пользователя от новостной рассылки.
    """
    def get(self, request, *args, **kwargs):
        # Если пользователь уже отписан
        if not request.user.profile.is_subscribed_to_newsletter: # Если используете UserProfile
        # if not request.user.is_subscribed_to_newsletter: # Если поле прямо в User
            messages.info(request, 'Вы уже отписаны от новостной рассылки.')
            return redirect('home') # Или куда-то еще

        context = {
            'email': request.user.email,
        }
        return render(request, 'boards/unsubscribe_confirm.html', context)

    def post(self, request, *args, **kwargs):
        # Отписываем пользователя
        # Если используете UserProfile:
        request.user.profile.is_subscribed_to_newsletter = False
        request.user.profile.save()
        # Если поле прямо в User:
        # request.user.is_subscribed_to_newsletter = False
        # request.user.save()

        messages.success(request, 'Вы успешно отписались от новостной рассылки.')
        return redirect('home') # Перенаправляем на главную страницу