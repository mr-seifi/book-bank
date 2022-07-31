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
    'account.apps.AccountConfig',
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
    'waiting_for_download': 'چند لحظه صبر کن تا برات پیداش کنم',
    'redirect_url': '*{title}* {authors} {publisher} {extension} {size} MB\n'
                    'برای دانلود کتابت، روی این '
                    '[لینک]({url})'
                    ' کلیک کن.',
    'limited_download': f'شرمنده ولی تا آخر امروز بیش‌تر از این نمی‌تونی از من کتاب دانلود کنی.',
    'start': 'سلام دوست عزیز \U0001F60D'
             '\n\n به بزرگترین بات دانلود کتاب زبان اصلی خوش اومدی، کافیه روی جستجوی کتاب کلیک کنی و کتاب موردنظرت رو پیدا کنی\!'
             '\n\n\U0001F536 اینجا فقط کتاب زبان اصلی داریم پس انگلیسی سرچ کن\.'
             '\n\n\U0001F536 ‌اگه کتابت توی نتایج پیدا نشد *اسم نویسنده کتاب* یا *منتشر کننده‌ی* اون رو هم کنارش بنویس تا بتونی پیداش کنی\.'
             '\n\n\U0001F514 [*به کانالمون یه سر بزن*](https://t.me/BookBank_Channel) \U0001F514',
    'payment': 'یکی از متدهای *پرداخت* زیر رو انتخاب کن.',
    'plan': 'یکی از *پلن‌های* زیر رو انتخاب کن.',
    'crypto_payment_network': 'به به، بچه مایه رو ببین، می‌خواد با کریپتو پرداخت کنه \U0001F923'
                              '\nیکی از *شبکه‌های* پرداختی زیر رو انتخاب کن.',
    'crypto_payment_deposit': 'حالا لطف کن مبلغ *{price} تتر* (کمیسیون حداکثر تا ۱ تتر پذیرفته می‌شود) رو به *ولت* \n`{wallet}‍`'
                              '\nبا شبکه `{network}` واریز کن. بعد از واریز کردن، *شناسه‌ی تراکنش‌ت* رو همینجا برام بفرست.',
    'crypto_payment_save': 'تشکر، حداکثر تا ۱۰ دقیقه دیگه نتیجه رو بهت اعلام می‌کنیم.',
    'approved_payment': 'تبریک میگم! تراکنشت تایید شد \U0001F929',
    'failed_payment': 'متاسفانه تراکنش‌ت تایید نشد،'
                      ' اگه واقعا پرداخت انجام داده بودی با دولوپر بات تماس بگیر @se1f1 \U0001F62A',
    'have_false_payment': 'شما هنوز یک تراکنش *تایید نشده* دارید، لطفا کمی صبر کنید.',
    'is_not_verified': 'من کلی کتاب دارم ولی برای اینکه بتونی ازم استفاده کنی باید توی کانال های زیر عضو بشی :)',
    'verified_start': 'به من خوش‌اومدی :)',
    'expired': 'خیلی دیر اقدام کردی، لطفا دوباره شروع کن \U0001F625',
    'expired_vip_user': 'متاسفانه باید بهت بگم که پلن وی‌آی‌پیت به اتمام رسیده \U0001F625،'
                        ' از طریق منو می‌تونی دوباره تمدیدش کنی. /start',
    'you_can\'t_do_it': 'دوباره تلاش کن \U0001F625',
    'help': 'اگه هنوز نمیدونی چطوری باید از بات استفاده کنی این فیلمو ببین! \U0001F469'
}

TELEGRAM_BUTTONS = {

}

STATES = {
    'start': 1,
    'payment': 85,
    'plan': 86,
    'crypto_payment': 87,
    'crypto_payment_trx': 88
}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

REGEX_PATTERNS = {
    'wallet_address': r'^(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|((bitcoincash|bchreg|bchtest):)'
                      r'?(q|p)[a-z0-9]{41}|0x[a-fA-F0-9]{40}|[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}'
                      r'|D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}|X[1-9A-HJ-NP-Za-km-z]'
                      r'{33}|4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}|A[0-9a-zA-Z]{33}|r[0-9a-zA-Z]{33}'
                      r'|(bnb)([a-z0-9]{39})|T[A-Za-z1-9]{33})$',
    'transaction_hash': r'0x\w{44,85}'
}

RELEASE_DATE = make_aware(datetime.datetime.strptime('2022-06-20 00:43:40', '%Y-%m-%d %H:%M:%S'))
DOWNLOAD_LIMIT_SIZE = int(3e7)
USER_DOWNLOAD_LIMIT = 10
