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
    'monitor-hardware-data': {
        'task': 'monitoring.tasks.monitor_hardware',
        'schedule': 30,
    },
    'delete-hardware-data': {
        'task': 'monitoring.tasks.delete_monitoring_data',
        'schedule': crontab(minute='0'),
    },
    'send-hardware-monitoring': {
        'task': 'monitoring.tasks.send_monitoring_data',
        'schedule': crontab(minute='*/5'),
    },
    'update-books': {
        'task': 'provider.tasks.libgen_task.update_database',
        'schedule': crontab(hour='5', minute='0')
    },
    'delete-account-limits': {
        'task': 'store.tasks.delete_account_limits',
        'schedule': crontab(hour='0', minute='0')
    },
    'monitor-account-limits': {
        'task': 'monitoring.tasks.monitor_account_limits',
        'schedule': 60,
    },
    'delete-account-limits-data': {
        'task': 'monitoring.tasks.delete_account_limits_data',
        'schedule': crontab(hour='0', minute='0'),
    },
    'send-account-limits-metrics': {
        'task': 'monitoring.tasks.send_account_limits_data',
        'schedule': crontab(minute='*/10'),
    },
    'monitor-queue': {
        'task': 'monitoring.tasks.monitor_queue',
        'schedule': 5,
    },
    'delete-queue': {
        'task': 'monitoring.tasks.delete_queue_data',
        'schedule': crontab(hour='0', minute='0'),
    },
    'send-queue-metrics': {
        'task': 'monitoring.tasks.send_queue_data',
        'schedule': crontab(minute='*/5'),
    },
}
