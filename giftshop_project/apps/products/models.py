from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    lat = models.FloatField()  # Vĩ độ (Tọa độ GIS)
    lng = models.FloatField()  # Kinh độ (Tọa độ GIS)
    phone = models.CharField(max_length=15)
    store_type = models.CharField(max_length=100, default="Gift Shop")
    revenue = models.IntegerField(default=0, verbose_name="Doanh thu (VNĐ)")

    def __str__(self):
        return self.name