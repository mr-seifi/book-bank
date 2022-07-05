"""
Django settings for book_bank project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from __future__ import absolute_import
import datetime
import os.path
from pathlib import Path
from django.utils.timezone import make_aware
from ..celery import app

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-luiy46)*#7b=7y_h@88(&w60j(n-_2-j-4_8)3umq0uvvm^i3v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'store.apps.StoreConfig',
    'provider.apps.ProviderConfig',
    'monitoring.apps.MonitoringConfig',
    'advertising.apps.AdvertisingConfig',
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

ROOT_URLCONF = 'book_bank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'book_bank.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration Options
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

TELEGRAM_MESSAGES = {
    'info': 'ببینید چه خبری آوردم!\n'
            '{info}',
    'warning': 'داستان داره میشه!!\n'
               '*{warning}*',
    'error': 'اوه اوه، نگفتم داستان میشه، چ کنیم حالا؟!!\n'
             '*{ex}*',
    'waiting_for_download': 'چند لحظه صبر کن ببینم می‌تونم پیداش کنم یا نه.',
    'redirect_url': '*{title}*\n_{year}-{extension}_\n{authors}-{publisher}\n\n{description}\n\n'
                    'برای دانلود کتاب، روی این '
                    '[لینک]({url})'
                    ' کلیک کن.',
    'limited_download': f'شرمنده ولی تا آخر امروز بیش‌تر از این نمی‌تونی از من کتاب دانلود کنی.',
    'start': 'سلام *عزیزم*! \U0001F60D'
             '\nچطوری؟ میدونستی سالیانه ۱۰ هزار نفر فقط کتاب می‌خونن؟'
             ' پس به خودت افتخار کن که با من آشنا شدی چون قراره به یه منبع نامحدودی از کتاب‌ها دسترسی پیدا کنی!'
             '\n\nکافیه اسم کتابی رو که می‌خوای سرچ کنی، '
             '‌اگه کتابت توی نتایج پیدا نشد اسم نویسنده کتاب یا منتشر کننده‌ی اون رو هم کنارش بنویس تا بتونی پیداش کنی.'
             '\n\n\U0001F514 *[تو کانالمون عضو شو](https://t.me/BookBank_Channel)* \U0001F514'
             '\n*بوس بهت* \U0001F618',

    'is_not_verified': 'سلام، به بوک‌بنک خوش‌اومدی :)\n'
                       'من کلی کتاب دارم ولی برای اینکه بتونی ازم *دانلود* کنی باید تو چند تا چنل عضو بشی که'
                       ' لینکشو برات این زیر میذارم.',
    'verified_start': 'به من خوش‌اومدی :)'
}

TELEGRAM_BUTTONS = {

}

STATES = {

}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

RELEASE_DATE = make_aware(datetime.datetime.strptime('2022-06-20 00:43:40', '%Y-%m-%d %H:%M:%S'))
DOWNLOAD_LIMIT_SIZE = int(3e7)
USER_DOWNLOAD_LIMIT = 10
