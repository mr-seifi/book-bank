# Generated by Django 4.0.5 on 2022-07-06 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_wallet_created_wallet_updated'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cryptopayment',
            options={},
        ),
        migrations.AlterModelOptions(
            name='shaparakpayment',
            options={},
        ),
        migrations.RemoveField(
            model_name='cryptopayment',
            name='transaction_id',
        ),
        migrations.RemoveField(
            model_name='shaparakpayment',
            name='transaction_id',
        ),
    ]
