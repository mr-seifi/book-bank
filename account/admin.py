from django.contrib import admin
from .models import Plan, Wallet


admin.site.register(Plan)
admin.site.redister(Wallet)
