from inventory.models import Inventory
from django.contrib import admin

from . import models

admin.site.register(models.Inventory)
admin.site.register(models.Requisition)