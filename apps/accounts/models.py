from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200, blank=True)

    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    province = models.CharField(max_length=100)

    district = models.CharField(max_length=100)

    ward = models.CharField(max_length=100)

    detail = models.CharField(max_length=255)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.detail}, {self.ward}, {self.district}, {self.province}"