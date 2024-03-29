from celery import shared_task
from .services import PaymentService
from _helpers.logging import logger
from django.conf import settings
from _helpers.telegram_service import InternalService
import asyncio


@shared_task(igonre_result=True)
def check_transactions():

    payment_service = PaymentService()

    # -- Check Has any Payment --
    if not payment_service.check_has_payments():
        return

    approved_payment_ids, failed_payment_ids = payment_service.validate_transactions()
    if approved_payment_ids:
        total_earned = payment_service.get_total_earned(payment_ids=approved_payment_ids)

        logger.info(
            f'*{len(approved_payment_ids)}* payments approved. - *{total_earned}$* earned.'
        )

        approved_payments_user_ids = payment_service.bulk_payment_id_to_user_id(payment_ids=approved_payment_ids)
        asyncio.run(InternalService.send_message_to_users(user_ids=approved_payments_user_ids,
                                                          message=settings.TELEGRAM_MESSAGES['approved_payment']))

    if failed_payment_ids:
        failed_payments_user_ids = payment_service.bulk_payment_id_to_user_id(payment_ids=failed_payment_ids)
        asyncio.run(InternalService.send_message_to_users(user_ids=failed_payments_user_ids,
                                                          message=settings.TELEGRAM_MESSAGES['failed_payment']))


@shared_task(ignore_result=True)
def check_expiration():

    payment_service = PaymentService()

    expired_users = payment_service.check_user_vip_expiration()
    user_ids = list(map(lambda x: x.user_id, expired_users))
    if expired_users:
        asyncio.run(InternalService.send_message_to_users(user_ids=user_ids,
                                                          message=settings.TELEGRAM_MESSAGES['expired_vip_user']))
