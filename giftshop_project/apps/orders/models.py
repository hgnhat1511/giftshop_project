from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    total_price = models.DecimalField(max_digits=10,decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=50,
        default="Pending"
    )