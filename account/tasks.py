from celery import shared_task
from .models import CryptoPayment
from .services import PaymentService
from django.utils import timezone
from _helpers.logging import logger
from django.db.models import Sum


@shared_task(igonre_result=True)
def check_transactions():
    payments = CryptoPayment.objects.filter(approved=False)
    payment_service = PaymentService()

    approved_payment_ids = []
    for payment in payments:
        is_validated = payment_service.validate_new_bsc_tx(tx_hash=payment.transaction_hash,
                                                           price=payment.plan.price)
        if is_validated:
            approved_payment_ids.append(payment.id)

    CryptoPayment.objects.filter(id__in=approved_payment_ids).update(approved=True)
    payments.filter(created__lte=timezone.now() - timezone.timedelta(hours=2)).delete()

    if approved_payment_ids:
        total_earned = CryptoPayment.objects.filter(id__in=approved_payment_ids).aggregate(
            Sum('plan__price')
        ).get('plan__price__sum', 0)

        logger.info(
            f'*{len(approved_payment_ids)}* payments approved. - *{total_earned}$* earned.'
        )
