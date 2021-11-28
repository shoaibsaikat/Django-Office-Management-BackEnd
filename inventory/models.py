from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from datetime import datetime

from django.db.models.fields import NullBooleanField

class Inventory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    unit = models.CharField(max_length=255, default='unit')
    count = models.PositiveIntegerField(blank=True, default=0)
    lastModifiedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Requisition(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE, related_name='requests')
    requestDate = models.DateTimeField(default=datetime.now)
    approver = models.ForeignKey(User, on_delete=CASCADE, related_name='requested_items')
    approved = models.BooleanField(null=True, blank=True, default=False)
    approveDate = models.DateTimeField(null=True)
    distributor = models.ForeignKey(User, on_delete=CASCADE, null=True, related_name='approved_items')
    distributed = models.BooleanField(null=True, blank=True, default=False)
    distributionDate = models.DateTimeField(null=True)
    title = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    # def get_absolute_url():
    #     pass
