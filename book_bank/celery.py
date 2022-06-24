import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

if os.environ.get('ENV') == 'dev':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_bank.settings.local')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_bank.settings.pro')

app = Celery('book_bank')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'monitoring.tasks.monitor_hardware',
        'schedule': 30,
    },
}
