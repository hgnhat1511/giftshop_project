from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify # Thêm để tạo link đẹp

# ==========================================
# 1. BẢNG DANH MỤC (MỚI THÊM)
# ==========================================
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, blank=True, null=True)

    # Tự động tạo slug (ví dụ: "Gấu bông" -> "gau-bong")
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# ==========================================
# 2. BẢNG SẢN PHẨM (ĐÃ THÊM CATEGORY)
# ==========================================
class Product(models.Model):
    name = models.CharField(max_length=200)
    
    # KẾT NỐI SẢN PHẨM VỚI DANH MỤC Ở ĐÂY
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products',
        verbose_name="Danh mục"
    )
    
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name

# ==========================================
# 3. BẢNG ĐÁNH GIÁ (GIỮ NGUYÊN)
# ==========================================
class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

# ==========================================
# 4. BẢNG CỬA HÀNG (GIỮ NGUYÊN)
# ==========================================
class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    lat = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    lng = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    phone = models.CharField(max_length=15)
    store_type = models.CharField(max_length=100, default="Gift Shop")
    revenue = models.IntegerField(default=0, verbose_name="Doanh thu (VNĐ)")

    def __str__(self):
        return self.name