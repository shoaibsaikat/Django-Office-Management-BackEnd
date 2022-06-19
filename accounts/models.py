from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver

TYPE_CHOICE = (
    (0, 'Officer'),
    (1, 'Pion'),
    (2, 'Typist'),
    (3, 'Driver'),
    (4, 'Consultant'),
    (20, 'Others'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=True, related_name='subordinates')
    canDistributeInventory = models.BooleanField(default=False, blank=True)
    canApproveInventory = models.BooleanField(default=False, blank=True)
    canApproveLeave = models.BooleanField(default=False, blank=True)
    canManageAsset = models.BooleanField(default=False, blank=True)
    phone1 = models.PositiveBigIntegerField(default=None, null=True, blank=True)
    phone2 = models.PositiveBigIntegerField(default=None, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICE, default=0)
    image = models.TextField(default='', blank=True)

    def __str__(self):
        return self.user.get_full_name()

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        try:
            profile = instance.profile
        except:
            profile = Profile.objects.create(user=instance)
        profile.save()

    def as_json(self):
        if self.user is not None:
            return dict(
                id=self.user.id,
                username=self.user.username,
                first_name=self.user.first_name, 
                last_name=self.user.last_name,
                email=self.user.email,
                manager_id=self.supervisor.id if self.supervisor is not None else None,
                can_distribute_inventory=self.canDistributeInventory,
                can_approve_inventory=self.canApproveInventory,
                can_approve_leave=self.canApproveLeave,
                can_manage_asset=self.canManageAsset,)
        else:
            return None
