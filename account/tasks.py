from celery import shared_task
from .models import CryptoPayment
from .services import PaymentService
from django.utils import timezone
from _helpers.logging import logger
from django.db.models import Sum
from django.conf import settings
from _helpers.telegram_service import InternalService
import asyncio


@shared_task(igonre_result=True)
def check_transactions():
    payments = CryptoPayment.objects.filter(approved=False, seen=False)
    payment_service = PaymentService()

    approved_payment_ids = []
    for payment in payments:
        is_validated = payment_service.validate_new_bsc_tx(tx_hash=payment.transaction_hash,
                                                           price=payment.plan.price)
        if is_validated:
            approved_payment_ids.append(payment.id)

    approved_payments = CryptoPayment.objects.filter(id__in=approved_payment_ids)
    approved_payments.update(approved=True,
                             seen=True)

    if approved_payment_ids:
        total_earned = CryptoPayment.objects.filter(id__in=approved_payment_ids).aggregate(
            Sum('plan__price')
        ).get('plan__price__sum', 0)

        logger.info(
            f'*{len(approved_payment_ids)}* payments approved. - *{total_earned}$* earned.'
        )

        approved_payments_user_ids = list(map(lambda pay: pay.user.user_id, approved_payments))
        asyncio.run(InternalService.send_message_to_users(user_ids=approved_payments_user_ids,
                                                          message=settings.TELEGRAM_MESSAGES['approved_payment']))

    failed_payments = payments
    if failed_payments.exists():
        failed_payments_user_ids = list(map(lambda pay: pay.user.user_id, failed_payments))
        asyncio.run(InternalService.send_message_to_users(user_ids=failed_payments_user_ids,
                                                          message=settings.TELEGRAM_MESSAGES['approved_payment']))
        failed_payments.update(seen=True)
