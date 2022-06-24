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
def send_monitoring_data(context=None):
    view = HardwareView()
    view.visualize()

    asyncio.create_task(InternalService.send_monitoring(context=context,
                                                        photo_path='hardware_usage.png',
                                                        caption='Hardware Usage'))


@shared_task
def clear_monitoring_data():
    service = MonitoringCacheService()

    service.delete_cpu()
    service.delete_memory()
