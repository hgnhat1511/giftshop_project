from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity