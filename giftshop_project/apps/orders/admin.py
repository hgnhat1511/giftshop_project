from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Các cột sẽ hiển thị ra bảng cho dễ nhìn
    list_display = ('id', 'user', 'product', 'quantity', 'status')
    
    # Thêm bộ lọc bên tay phải để lọc đơn Giỏ hàng / Đang xử lý
    list_filter = ('status',)