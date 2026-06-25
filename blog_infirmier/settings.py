"""
Django settings for blog_infirmier project.
Configuration complète pour développement et production.
Audit sécurité appliqué — version finale.
"""

from pathlib import Path
import os
from decouple import config

# ===========================================================
# CHEMINS
# ===========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================================
# SÉCURITÉ DE BASE
# ===========================================================
SECRET_KEY = config('SECRET_KEY')

# Validation de la SECRET_KEY
if len(SECRET_KEY) < 50:
    raise Exception("SECRET_KEY trop courte ou non définie dans le fichier .env !")

DEBUG = config('DEBUG', default=False, cast=bool)

# Bloquer DEBUG=True en production
if DEBUG and 'pythonanywhere.com' in config('SITE_URL', default=''):
    raise Exception("DEBUG ne doit pas être True en production !")

# ALLOWED_HOSTS selon environnement
ALLOWED_HOSTS = (
    ['127.0.0.1', 'localhost', 'infirmierblog.pythonanywhere.com']
    if DEBUG
    else ['infirmierblog.pythonanywhere.com']
)

# CSRF — requis en production HTTPS
CSRF_TRUSTED_ORIGINS = ['https://infirmierblog.pythonanywhere.com']

# ===========================================================
# APPLICATIONS
# ===========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    # Third-party apps
    'ckeditor',
    'ckeditor_uploader',
    'taggit',
    'django_ratelimit',

    # Local apps
    'accounts',
    'blog',
    'resources',
    'contact',
    'newsletter',
    'dashboard',
    'core',
]

# ===========================================================
# MIDDLEWARE
# ===========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================================================
# URLS & WSGI
# ===========================================================
ROOT_URLCONF = 'blog_infirmier.urls'
WSGI_APPLICATION = 'blog_infirmier.wsgi.application'

# ===========================================================
# TEMPLATES
# ===========================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.global_context',
            ],
        },
    },
]

# ===========================================================
# BASE DE DONNÉES
# ===========================================================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        'CONN_MAX_AGE': 60,
    }
}

# ===========================================================
# CACHE — LocMemCache (pas de fichier disque, plus sécurisé)
# Compatible avec django-ratelimit
# ===========================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ===========================================================
# AUTHENTIFICATION
# ===========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'auth.User'
LOGIN_URL = '/accounts/connexion/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Sessions — expiration depuis dernière activité
SESSION_COOKIE_AGE = 3600              # 1 heure
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True      # Renouvelle à chaque requête

# ===========================================================
# INTERNATIONALISATION
# ===========================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# ===========================================================
# FICHIERS STATIQUES & MÉDIAS
# ===========================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Limite de taille des uploads (5 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

# ===========================================================
# DIVERS
# ===========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================================
# CKEDITOR
# ===========================================================
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_ALLOW_NONIMAGE_FILES = False  # Sécurité : images uniquement

CKEDITOR_CONFIGS = {

    # Config publique — sans Source (utilisateurs)
    'default': {
        'skin': 'moono-lisa',
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            '/',
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
        ],
        'toolbar': 'YourCustomToolbarConfig',
        'height': 400,
        'width': '100%',
        'tabSpaces': 4,
        'disallowedContent': 'script *; *[on*]; iframe *; frame *; object *; embed *;',
        'contentsCss': ['/static/css/article_content.css'],
        'extraPlugins': ','.join([
            'uploadimage', 'div', 'autolink', 'autoembed',
            'embedsemantic', 'autogrow', 'widget', 'lineutils',
            'clipboard', 'dialog', 'dialogui', 'elementspath',
        ]),
    },

    # Config djiba — avec Source HTML pour l'administrateur
    'djiba': {
        'skin': 'moono-lisa',
        'toolbar_DjibaToolbar': [
            {'name': 'document', 'items': ['Source', '-', 'NewPage', 'Preview']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            '/',
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Blockquote', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
        ],
        'toolbar': 'DjibaToolbar',
        'height': 400,
        'width': '100%',
        'tabSpaces': 4,
        'disallowedContent': 'script *; *[on*];',
        'contentsCss': ['/static/css/article_content.css'],
        'extraPlugins': ','.join([
            'sourcearea',
            'uploadimage', 'div', 'autolink', 'autoembed',
            'embedsemantic', 'autogrow', 'widget', 'lineutils',
            'clipboard', 'dialog', 'dialogui', 'elementspath',
        ]),
    },
}

# ===========================================================
# EMAIL
# ===========================================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Blog Infirmier <noreply@bloginfirmier.com>')
CONTACT_EMAIL = config('CONTACT_EMAIL')

# ===========================================================
# TAGGIT
# ===========================================================
TAGGIT_CASE_INSENSITIVE = True

# ===========================================================
# LOGGING
# ===========================================================
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django_errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ===========================================================
# SÉCURITÉ PRODUCTION
# ===========================================================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# ===========================================================
# PAGINATION
# ===========================================================
ARTICLES_PER_PAGE = 9
COMMENTS_PER_PAGE = 10

# ===========================================================
# INFOS SITE
# ===========================================================
SITE_NAME = "Blog Infirmier de Santé Publique"
SITE_DESCRIPTION = "Plateforme dédiée à la santé publique, l'épidémiologie et la santé numérique"
SITE_AUTHOR = "Infirmier de Santé Publique"
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# ===========================================================
# RATE LIMITING
# ===========================================================
SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003']
RATELIMIT_USE_CACHE = 'default'