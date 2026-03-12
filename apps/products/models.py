from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):

    name = models.CharField(max_length=200)

    price = models.IntegerField()

    stock = models.IntegerField(default=0)

    description = models.TextField()

    image = models.ImageField(upload_to='products/',null=True)

    def __str__(self):
        return self.name

class Rating(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    stars = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)