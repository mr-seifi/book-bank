from celery import shared_task
from .services.cache_service import MonitoringCacheService
from _helpers.telegram_service import InternalService
from .views import HardwareView
import asyncio


@shared_task(ignore_result=True)
def monitor_hardware():
    service = MonitoringCacheService()

    service.cache_cpu()
    service.cache_memory()


@shared_task(ignore_result=True)
def send_monitoring_data(context=None):
    view = HardwareView()
    view.visualize()

    asyncio.run(InternalService.send_monitoring(context=context,
                                                photo_path='hardware_usage.png',
                                                caption='Hardware Usage'))


@shared_task(ignore_result=True)
def delete_monitoring_data():
    service = MonitoringCacheService()

    service.delete_cpu()
    service.delete_memory()
