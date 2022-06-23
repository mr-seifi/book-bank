from django.db import models


class ZlibAccount(models.Model):
    user_id = models.IntegerField()
    user_key = models.CharField(max_length=50)
