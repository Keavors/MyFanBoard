# MyFanBoard/boards/forms.py

from django import forms
from .models import Post, Response
from django_ckeditor_5.widgets import CKEditor5Widget # Импортируем CKEditor5Widget
from .models import Post, Response, Newsletter # Добавьте Newsletter

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок вашего поста'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default') # Используем CKEditor5Widget
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
        }

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['content'] # Только поле content, так как post и author будут заполняться автоматически
        widgets = {
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default') # Используем CKEditor5Widget
        }
        labels = {
            'content': 'Ваш ответ',
        }


class NewsletterForm(forms.ModelForm):
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