from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('cart', 'Trong giỏ hàng'),
        ('pending', 'Chờ xử lý'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # Khách mua món gì?
    quantity = models.PositiveIntegerField(default=1) # Mua bao nhiêu món?
    
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # --- TRƯỜNG MỚI THÊM: Lưu địa chỉ giao hàng (từ sổ địa chỉ, nhập tay, hoặc bản đồ) ---
    shipping_address = models.CharField(max_length=500, null=True, blank=True, verbose_name="Địa chỉ giao hàng")
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.status})"