from celery import shared_task
from .services.cache_service import MonitoringCacheService
from _helpers.telegram_service import InternalService
from .views import HardwareView
import asyncio


@shared_task
def monitor_hardware():
    service = MonitoringCacheService()

    service.cache_cpu()
    service.cache_memory()


@shared_task
def send_monitoring_data(context):
    view = HardwareView()
    view.visualize_cpu_usage()

    asyncio.run(InternalService.send_monitoring(context=context,
                                                photo_path='cpu_usage.png',
                                                caption='CPU Usage'))
