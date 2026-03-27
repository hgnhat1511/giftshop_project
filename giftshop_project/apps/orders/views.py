from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Order
from apps.products.models import Product

# ==========================================
# PHẦN 1: DÀNH CHO KHÁCH HÀNG (GIỎ HÀNG & ĐƠN HÀNG)
# ==========================================

@login_required
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ hàng (Gán cứng status='cart')"""
    product = get_object_or_404(Product, id=product_id)
    
    order_item, created = Order.objects.get_or_create(
        user=request.user,
        product=product,
        status='cart',
        defaults={'quantity': 1}
    )
    
    if not created:
        order_item.quantity += 1
        order_item.save()
        
    messages.success(request, f"Đã thêm {product.name} vào giỏ hàng!")
    return redirect('view_cart')

@login_required
def view_cart(request):
    """Hiển thị các món hàng đang nằm trong giỏ (status='cart')"""
    cart_items = Order.objects.filter(user=request.user, status='cart')
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def my_orders(request):
    """Hiển thị lịch sử đơn hàng (status khác 'cart')"""
    # Lưu ý: Đảm bảo model Order của bạn có trường created_at, nếu không hãy đổi thành -id
    orders = Order.objects.filter(user=request.user).exclude(status='cart').order_by('-id')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def checkout(request):
    """Chuyển toàn bộ hàng trong giỏ sang trạng thái chờ xử lý (pending)"""
    cart_items = Order.objects.filter(user=request.user, status='cart')
    
    if cart_items.exists():
        cart_items.update(status='pending') 
        messages.success(request, "Thanh toán thành công! Đơn hàng đang được xử lý.")
        return redirect('my_orders')
        
    messages.warning(request, "Giỏ hàng của bạn đang trống!")
    return redirect('view_cart')

# ==========================================
# PHẦN 2: DÀNH CHO ADMIN (QUẢN LÝ ĐƠN HÀNG)
# ==========================================

@staff_member_required
def admin_orders(request):
    """Trang danh sách toàn bộ đơn hàng cho ADMIN"""
    orders = Order.objects.all().order_by('-id')
    return render(request, 'orders/admin_order_list.html', {'orders': orders})

@staff_member_required
def update_order_status(request, id):
    """Xử lý nút bấm Cập nhật trạng thái đơn hàng"""
    if request.method == "POST":
        order = get_object_or_404(Order, id=id)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f"Đã cập nhật trạng thái đơn hàng #{order.id}!")
    return redirect('admin_orders')