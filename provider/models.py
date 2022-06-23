from django.db import models
from .services.zlib_service import ZLibCache


class ZlibAccount(models.Model):
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)
    user_id = models.IntegerField(max_length=20)
    user_key = models.CharField(max_length=50)

    @staticmethod
    def get_available_account():
        service = ZLibCache()
        account_id = service.get_available()

        if service.get_limit(account_id) < service.LIMIT:
            return ZlibAccount.objects.get(pk=account_id)

        for account in ZlibAccount.objects.all():
            if service.get_limit(account_id=account.id) < service.LIMIT:
                service.cache_available(account_id=account.id)
                return account
