from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from apps.products.models import Product, Store
from apps.orders.models import Order

@staff_member_required
def dashboard_view(request): # Đã đổi tên từ 'dashboard' thành 'dashboard_view'
    """Trang thống kê tổng quan dành cho Admin"""
    # Đếm tổng sản phẩm
    total_products = Product.objects.count()
    
    # Đếm tổng số món hàng đang nằm trong giỏ (status='cart')
    total_cart_items = Order.objects.filter(status='cart').count()
    
    # Đếm tổng đơn hàng đã đặt (status='pending')
    total_orders = Order.objects.filter(status='pending').count()
    
    # Tính tổng doanh thu từ 101 cửa hàng
    total_revenue = sum(store.revenue for store in Store.objects.all())

    context = {
        'total_products': total_products,
        'total_cart_items': total_cart_items,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard/dashboard.html', context)