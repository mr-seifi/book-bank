from django.db import models
from django.utils import timezone


class User(models.Model):

    class LanguageChoices(models.TextChoices):
        english = 'en', 'ENGLISH'
        persian = 'fa', 'PERSIAN'

    user_id = models.CharField(max_length=15, db_index=True, unique=True)
    username = models.CharField(max_length=100, null=True)
    fullname = models.CharField(max_length=250, null=True)
    language = models.CharField(max_length=5, choices=LanguageChoices.choices, default=LanguageChoices.persian)
    plan = models.ForeignKey(to='Plan', on_delete=models.CASCADE, related_name='users', null=True)

    def is_vip(self) -> bool:
        if not self.cryptopayments.filter(approved=True).exists() or \
                not self.shaparakpayments.filter(approved=True).exists():
            return False
        last_payment = (self.cryptopayments.filter(approved=True) or self.shaparakpayments.filter(approved=True)).last()
        if last_payment.created + timezone.timedelta(days=last_payment.plan.interval) < timezone.now():
            return False
        return True


class Plan(models.Model):

    class ModeChoices(models.TextChoices):
        shaparak = 'shaparak', 'SHAPARAK'
        cryptocurrency = 'cryptocurrency', 'CRYPTOCURRENCY'

    name = models.CharField(max_length=50)
    mode = models.CharField(max_length=15, choices=ModeChoices.choices)
    interval = models.IntegerField()  # Days
    price = models.IntegerField()  # Toman/Tether
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        base = f'پلن {self.name} - {self.interval} روزه - {self.price} '
        return base + ('تومان', 'تتر')[self.mode == 'cryptocurrency']


class BasePayment(models.Model):

    user = models.ForeignKey(to='User', on_delete=models.PROTECT, related_name='%(class)ss')
    plan = models.ForeignKey(to='Plan', on_delete=models.PROTECT, related_name='%(class)ss')
    transaction_hash = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ShaparakPayment(BasePayment):
    ...


class CryptoPayment(BasePayment):

    wallet = models.ForeignKey(to='Wallet', on_delete=models.PROTECT)
    seen = models.BooleanField(default=False)


class Wallet(models.Model):

    class NetworkChoices(models.TextChoices):
        erc_20 = 'erc-20', 'ERC-20'
        trc_20 = 'trc-20', 'TRC-20'
        bep_20 = 'bep-20', 'BEP-20'

    network = models.CharField(max_length=10, choices=NetworkChoices.choices)
    address = models.CharField(max_length=256, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
