from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'book_bank_local_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres'
    }
}
