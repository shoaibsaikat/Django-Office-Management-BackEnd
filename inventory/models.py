from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from datetime import datetime

class Inventory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    unit = models.CharField(max_length=255, default='unit')
    count = models.PositiveIntegerField(blank=True, default=0)
    lastModifiedDate = models.DateTimeField(auto_now=True)

    def as_json(self):
        return dict(
            id=self.pk,
            name=self.name,
            unit=self.unit,
            count=self.count,
            description=self.description,)

    def as_minimum_json(self):
        return dict(
            id=self.pk,
            name=self.name,
            unit=self.unit,
            count=self.count,)

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

    def as_json(self):
        return dict(
            id=self.pk,
            user=self.user.pk,
            user_name=self.user.first_name + ' ' + self.user.last_name,
            item_name=self.inventory.name,
            unit=self.inventory.unit,
            total=self.inventory.count,
            approver=self.approver.pk if self.approver is not None else None,
            approver_name = self.approver.first_name + ' ' + self.approver.last_name if self.approver is not None else None,
            distributor=self.distributor.pk if self.distributor is not None else None,
            distributor_name = self.distributor.first_name + ' ' + self.distributor.last_name if self.distributor is not None else None,
            approved=self.approved,
            distributed=self.distributed,
            title=self.title,
            amount=self.amount,
            comment=self.comment,
            date=str(self.requestDate),)

    def __str__(self):
        return self.title

