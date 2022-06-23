from django.db import models
from .services.zlib_service import ZLibCache


class ZlibAccount(models.Model):
    user_id = models.IntegerField()
    user_key = models.CharField(max_length=50)

    @staticmethod
    def get_available_account():
        service = ZLibCache()
        account_id = service.get_available()
        if not account_id:
            account_id = 1

        if service.get_limit(account_id) < service.LIMIT:
            return ZlibAccount.objects.get(pk=account_id)

        for account in ZlibAccount.objects.all():
            if service.get_limit(account_id=account.id) < service.LIMIT:
                service.cache_available(account_id=account.id)
                return account
