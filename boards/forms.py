from django import forms
from .models import Post, Response, Newsletter
from django_ckeditor_5.widgets import CKEditor5Widget

class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования постов.
    """
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок вашего поста'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default')
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
        }

class ResponseForm(forms.ModelForm):
    """
    Форма для создания откликов на посты.
    """
    class Meta:
        model = Response
        fields = ['content']
        widgets = {
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default')
        }
        labels = {
            'content': 'Ваш ответ',
        }


class NewsletterForm(forms.ModelForm):
    """
    Форма для создания новостной рассылки.
    """
    class Meta:
        model = Newsletter
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема рассылки'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default')
        }
        labels = {
            'subject': 'Тема',
            'content': 'Содержание рассылки',
        }