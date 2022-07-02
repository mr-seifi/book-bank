from celery import shared_task
from .services.cache_service import MonitoringCacheService, MetricsCacheService
from _helpers.telegram_service import InternalService
from .views import HardwareView, MetricsView
import asyncio


@shared_task(ignore_result=True)
def monitor_hardware():
    service = MonitoringCacheService()

    service.cache_cpu()
    service.cache_memory()


@shared_task(ignore_result=True)
def send_monitoring_data(context=None):
    view = HardwareView()
    view.visualize_hardware()

    asyncio.run(InternalService.send_monitoring(context=context,
                                                photo_path='hardware_usage.png',
                                                caption='Hardware Usage'))


@shared_task(ignore_result=True)
def delete_monitoring_data():
    service = MonitoringCacheService()

    service.delete_cpu()
    service.delete_memory()


@shared_task(ignore_result=True)
def monitor_account_limits():
    service = MetricsCacheService()

    service.cache_account_limits()


@shared_task(ignore_result=True)
def send_account_limits_data(context=None):
    view = MetricsView()
    view.visualize_account_limits()

    asyncio.run(InternalService.send_monitoring(context=context,
                                                photo_path='account_limits.png',
                                                caption='Account Limits'))


@shared_task(ignore_result=True)
def delete_account_limits_data():
    service = MetricsCacheService()

    service.delete_account_limits()


@shared_task(ignore_result=True)
def monitor_queue():
    service = MetricsCacheService()

    service.cache_queue()


@shared_task(ignore_result=True)
def send_queue_data(context=None):
    view = MetricsView()
    view.visualize_queue()

    asyncio.run(InternalService.send_monitoring(context=context,
                                                photo_path='queue.png',
                                                caption='Queue'))


@shared_task(ignore_result=True)
def delete_queue_data():
    service = MetricsCacheService()

    service.delete_queue()
