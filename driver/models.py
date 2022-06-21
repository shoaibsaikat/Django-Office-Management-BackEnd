from django.db import models
from django.db.models.deletion import CASCADE

from accounts.models import User
from asset.models import Asset

class Route(models.Model):
    name = models.CharField(max_length=255, blank=False)
    driver = models.ForeignKey(User, on_delete=CASCADE, null=True, related_name='drivers')
    car = models.ForeignKey(Asset, on_delete=CASCADE, null=True, related_name='cars')
    creationDate = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default='', blank=False)
    active = models.BooleanField(default=False, blank=False)

    def as_json(self):
        return dict(
            id=self.pk,
            driver=self.driver.pk,
            driver_first_name=self.driver.first_name,
            driver_last_name=self.driver.last_name,
            car=self.car.pk,
            model=self.car.model,
            number=self.car.serial,
            acitve=self.active,
            description=self.description,)

    def __str__(self):
        return self.name

class RouteUser(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, blank=False, related_name='users')
    route = models.ForeignKey(Route, on_delete=CASCADE, blank=False, related_name='routes')

    def as_json(self):
        return dict(
            id=self.pk,
            user=self.user.pk,
            route=self.route.pk,)

    def __str__(self):
        return self.pk
