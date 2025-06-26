from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.http import Http404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Board, Post, Response
from .forms import PostForm, ResponseForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# --- Представления для досок ---
def board_list(request):
    """
    Отображает список всех досок объявлений.
    """
    boards = Board.objects.all()
    return render(request, 'boards/board_list.html', {'boards': boards})

def posts_by_board(request, pk):
    """
    Отображает список постов для выбранной доски.
    """
    board = get_object_or_404(Board, pk=pk)
    posts = Post.objects.filter(board=board).order_by('-created_at')
    return render(request, 'boards/posts_by_board.html', {'board': board, 'posts': posts})

# --- Представления для постов ---
@login_required
def create_post(request, pk):
    """
    Создает новый пост на указанной доске.
    Требует аутентификации пользователя.
    """
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.board = board
            post.author = request.user
            post.save()
            messages.success(request, 'Ваш пост успешно создан!')
            return redirect('boards:post_detail', board_pk=board.pk, post_pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'boards/post_create.html', {'form': form, 'board': board})

def post_detail(request, board_pk, post_pk):
    """
    Отображает детали конкретного поста и список откликов к нему.
    Увеличивает счетчик просмотров поста.
    """
    post = get_object_or_404(Post, board__pk=board_pk, pk=post_pk)

    # Увеличение счетчика просмотров.
    Post.objects.filter(pk=post_pk).update(views=F('views') + 1)
    post.refresh_from_db()

    responses = Response.objects.filter(post=post).order_by('created_at')
    form = ResponseForm()

    return render(request, 'boards/post_detail.html', {
        'post': post,
        'responses': responses,
        'form': form
    })

@login_required
def add_response(request, board_pk, post_pk):
    """
    Добавляет новый отклик к посту.
    Требует аутентификации пользователя.
    """
    post = get_object_or_404(Post, board__pk=board_pk, pk=post_pk)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.post = post
            response.author = request.user
            response.save()
            messages.success(request, 'Ваш ответ успешно добавлен!')
            return redirect(reverse('boards:post_detail', args=[board_pk, post_pk]) + '#responses')
    else:
        return redirect('boards:post_detail', board_pk=board_pk, post_pk=post_pk)

    return render(request, 'boards/post_detail.html', {'form': form, 'post': post})


@login_required
def edit_post(request, board_pk, post_pk):
    """
    Редактирует существующий пост.
    Доступно только автору поста.
    """
    post = get_object_or_404(Post, board__pk=board_pk, pk=post_pk)

    # Проверка прав пользователя на редактирование.
    if request.user != post.author:
        messages.error(request, 'У вас нет прав для редактирования этого поста.')
        return redirect('boards:post_detail', board_pk=board_pk, post_pk=post_pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('boards:post_detail', board_pk=board_pk, post_pk=post_pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'boards/post_edit.html', {'form': form, 'post': post, 'board': post.board})

@login_required
def my_posts_responses_view(request):
    """
    Отображает отклики на объявления, созданные текущим пользователем.
    Позволяет фильтровать отклики по конкретным объявлениям.
    """
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    selected_post_id = request.GET.get('post')

    responses = Response.objects.filter(post__author=request.user).order_by('-created_at')

    if selected_post_id:
        try:
            selected_post = user_posts.get(pk=selected_post_id)
            responses = responses.filter(post=selected_post)
            messages.info(request, f'Отклики отфильтрованы по посту: "{selected_post.title}"')
        except Post.DoesNotExist:
            messages.error(request, 'Выбранный пост не существует или не принадлежит вам.')
            selected_post_id = None
            responses = Response.objects.filter(post__author=request.user).order_by('-created_at')

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
    Принимает отклик на пост.
    Только автор поста может принять отклик на свой пост.
    Отправляет уведомление автору отклика.
    """
    response = get_object_or_404(Response, pk=pk)

    # Проверка прав пользователя на принятие отклика.
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

            # Отправка уведомления автору отклика.
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

    return redirect('boards:my_posts_responses')


@login_required
def delete_response_view(request, pk):
    """
    Удаляет отклик.
    Только автор поста может удалить отклик.
    """
    response = get_object_or_404(Response, pk=pk)

    # Проверка прав пользователя на удаление отклика.
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
        # Проверка, подписан ли пользователь на рассылку.
        if not request.user.profile.is_subscribed_to_newsletter:
            messages.info(request, 'Вы уже отписаны от новостной рассылки.')
            return redirect('home')

        context = {
            'email': request.user.email,
        }
        return render(request, 'boards/unsubscribe_confirm.html', context)

    def post(self, request, *args, **kwargs):
        # Отписка пользователя от рассылки.
        request.user.profile.is_subscribed_to_newsletter = False
        request.user.profile.save()

        messages.success(request, 'Вы успешно отписались от новостной рассылки.')
        return redirect('home')