from django.contrib import admin
from .models import Product, Category, Rating, Store

# Đăng ký Danh mục
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
# Đăng ký Sản phẩm
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Rating)
admin.site.register(Store)