from django.contrib import admin
from .models import Product, Category, Rating, Store, ProductImage

# 1. Đăng ký Danh mục
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# 2. Tạo khu vực upload nhiều ảnh (Phải viết TRƯỚC class ProductAdmin)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Số lượng ảnh mặc định khi thêm mới sản phẩm, có thể thay đổi tùy ý

# 3. Đăng ký Sản phẩm
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
    # Gọi cái Inline chụp ảnh vào đây
    inlines = [ProductImageInline]

# 4. Đăng ký các model khác
admin.site.register(Rating)
admin.site.register(Store)