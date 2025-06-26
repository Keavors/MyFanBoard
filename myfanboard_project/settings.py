"""
Настройки Django для проекта myfanboard_project.

Дополнительную информацию об этом файле см.:
https://docs.djangoproject.com/en/5.2/topics/settings/

Полный список настроек и их значений см.:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path


# Построение путей внутри проекта: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Настройки для быстрой разработки — непригодны для продакшена.
# Подробнее см.: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: держите секретный ключ в продакшене в тайне!
SECRET_KEY = 'django-insecure-(1u3)6wz03$=3m3xsgw)vl=uzfzdwff0qa*%045bj1o#51*=eu'

# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: не запускайте с включенным режимом отладки в продакшене!
DEBUG = True

ALLOWED_HOSTS = []


# Определение приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'main',
    'boards',
    'django_ckeditor_5',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myfanboard_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myfanboard_project.wsgi.application'


# База данных
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Валидация пароля
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Интернационализация
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Статические файлы (CSS, JavaScript, Изображения)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

# Тип поля первичного ключа по умолчанию
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки EMAIL
# Для разработки письма будут выводиться в консоль.
# В продакшене необходимо настроить реальный SMTP-сервер.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@myfanboard.com' # Email, от которого будут отправляться письма
SERVER_EMAIL = DEFAULT_FROM_EMAIL # Email для серверных сообщений (ошибки и т.д.)
SITE_URL = 'http://127.0.0.1:8000'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Настройки CKEditor 5
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', '|',
                    'imageUpload', 'mediaEmbed', 'undo', 'redo'],
    },
    'extends': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', '|',
                    'imageUpload', 'blockQuote', 'mediaEmbed', '|',
                    'undo', 'redo'],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:full', 'imageStyle:alignRight'],
            'styles': [
                'full',
                'alignLeft',
                'alignRight'
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells']
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'}
            ]
        }
    },
    'list': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', '|',
                    'imageUpload', 'blockQuote', 'mediaEmbed', 'undo', 'redo']
    }
}

CKEDITOR_5_UPLOAD_PATH = "uploads/" # Папка для загрузки файлов внутри MEDIA_ROOT.
CKEDITOR_5_FILE_STORAGE = 'django_ckeditor_5.storage.DefaultStorage' # Использование хранилища по умолчанию.

# Дополнительные настройки для CKEditor 5, которые могут помочь с разрешениями:
# CKEDITOR_5_UPLOAD_VIEW_CHECK_PERMISSIONS = True # По умолчанию True. Если True, то разрешения DRF будут работать.
# Если False, то Django не будет проверять разрешения.

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FileUploadParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ]
}

CKEDITOR_5_UPLOAD_VIEW_CHECK_PERMISSIONS = False