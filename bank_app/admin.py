from django.contrib import admin
from .models import Bank_Model, Transaction_Model

# Register your models here.
admin.site.register(Bank_Model)
admin.site.register(Transaction_Model)