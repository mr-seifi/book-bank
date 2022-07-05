from django.db import models


class Advertiser(models.Model):

    channel_name = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expired = models.DateTimeField(null=True)
