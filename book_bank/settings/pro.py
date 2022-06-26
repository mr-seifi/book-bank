from .base import *

DEBUG = False

ADMINS = (
    ('Amin Seifi', 'aminseiifi@gmail.com'),
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'book_bank_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres'
    }
}
