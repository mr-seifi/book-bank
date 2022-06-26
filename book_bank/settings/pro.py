from .base import *

DEBUG = False

ADMINS = (
    ('Amin Seifi', 'aminseiifi@gmail.com'),
)

ALLOWED_HOSTS = ['book-bank.net', 'www.book-bank.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'book_bank_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres'
    }
}
