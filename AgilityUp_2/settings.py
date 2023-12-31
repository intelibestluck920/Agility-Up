"""
Django settings for AgilityUp_2 project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import environ
import os

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sx*ih#3182t0=0haz)8z3x4t#hq1m9%8%*r*$(q0g-z1$8m1f6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['dev.api.agilityup.ai', '127.0.0.1', 'api.agilityup.ai']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom apps
    'accounts.apps.AccountsConfig',
    'core.apps.CoreConfig',
    'invites.apps.InvitesConfig',
    'product.apps.ProductConfig',
    'permissions.apps.PermissionsConfig',

    # third party packages
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'drf_yasg',
    'corsheaders',
    'django_crontab',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AgilityUp_2.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'AgilityUp_2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'agilityup_db',        
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
        # 'USER': 'agilityup_user',
        # 'PASSWORD': 'tAFwAV9okVYi6Hvogu4Z',
        # 'HOST': 'localhost',
        # 'PORT': '',
        # 'NAME': 'agilityup_db',
        # 'USER': 'agilityup_user',
        # 'PASSWORD': 'tAFwAV9okVYi6Hvogu4Z',
        # 'HOST': '3.212.195.106',
        # 'PORT': '',
    }
}

# yes yes yes

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# custom user declaration
AUTH_USER_MODEL = 'accounts.User'

# allauth config

AUTHENTICATION_BACKENDS = [
    # allauth specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    # Needed to login by username in Django admin, regardless of allauth
    'django.contrib.auth.backends.ModelBackend',
]

SITE_ID = 1
REST_USE_JWT = True

JWT_AUTH_COOKIE = 'my-app-auth'

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = None

LOGIN_REDIRECT_URL = 'core:api-overview'

LOGIN_URL = 'rest_login'

# dj-rest-auth config

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer',
}

REST_AUTH_SERIALIZERS = {
    'PASSWORD_RESET_SERIALIZER':
        'accounts.serializers.CustomPasswordResetSerializer',
    'TOKEN_SERIALIZER': 'accounts.serializers.TokenSerializer',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        #'rest_framework.authentication.TokenAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
}

REST_SESSION_LOGIN = True

# Email Setup
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'agility.up.ai.test@gmail.com'
EMAIL_HOST_PASSWORD = 'ghxbbavilyctftxt'

DEFAULT_FROM_EMAIL = 'noreply<agility.up.ai.test@gmail.com>'

# REST_AUTH_TOKEN_MODEL = None

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "key",
]

# # frontend  url definition
URL_FRONT = 'http://www.agilityup.ai/'
# ACCOUNT_EMAIL_CONFIRMATION_URL = URL_FRONT + 'confirm-email/'
# ACCOUNT_PASSWORD_RESET_CONFIRM = URL_FRONT + 'change-password/'
#
# # override default adapter
#
# ACCOUNT_ADAPTER="accounts.adapter.AccountAdapter"


# cron job setting: runs at midnight
CRONJOBS = [
    ('0 0 * * *', 'core.cron.create_sprint_periodic', '>>' + os.path.join(BASE_DIR, "cron_logs.txt")),
    ('0 0 * * *', 'core.cron.alert_sprint_expire', '>>' + os.path.join(BASE_DIR, "cron_logs.txt")),
    ('0 0 * * *', 'core.cron.alert_feedback', '>>' + os.path.join(BASE_DIR, "cron_logs.txt")),
]


