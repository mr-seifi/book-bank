# Generated by Django 4.0.5 on 2022-07-06 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_cryptopayment_transaction_hash_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptopayment',
            name='transaction_hash',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='shaparakpayment',
            name='transaction_hash',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]
