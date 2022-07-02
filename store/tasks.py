import logging
from .services import AccountCacheService
from celery import shared_task

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(process)d-%(filename)s-%(lineno)s-%(levelname)s-%(message)s')


@shared_task(ignore_result=True)
def delete_account_limits():
    service = AccountCacheService()

    service.delete_limits()
    logger.info('account limits were deleted!')

