from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product # Kết nối với sản phẩm

class Order(models.Model):
    # Các trạng thái để quản lý vòng đời đơn hàng
    STATUS_CHOICES = (
        ('cart', 'Trong giỏ hàng'),
        ('pending', 'Chờ xử lý'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # Khách mua món gì?
    quantity = models.PositiveIntegerField(default=1) # Mua bao nhiêu món?
    
    # Giá tại thời điểm mua (đề phòng sau này Nhật đổi giá sản phẩm)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="cart" # Mặc định là nằm trong giỏ hàng
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.status})"