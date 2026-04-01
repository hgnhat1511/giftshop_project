from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Order
from apps.products.models import Product
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string # Thêm để đọc file HTML
from django.utils.html import strip_tags # Thêm để tạo bản backup chữ thô
import threading

# ==========================================
# HÀM PHỤ TRỢ: GỬI MAIL CHẠY NGẦM (ASYNC)
# ==========================================
def send_email_thread(subject, html_content, recipient_list):
    """Hàm này giúp gửi mail HTML ở một luồng riêng, không làm treo giao diện web"""
    # Tạo bản backup chữ thô từ HTML đề phòng mail client không hỗ trợ HTML
    text_content = strip_tags(html_content)
    
    send_mail(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=True,
        html_message=html_content, # Gửi giao diện HTML ở đây
    )

# ==========================================
# PHẦN 1: DÀNH CHO KHÁCH HÀNG (GIỎ HÀNG & ĐƠN HÀNG)
# ==========================================

@login_required
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ với số lượng tùy chọn + Kiểm tra kho"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
    else:
        quantity = 1

    if product.stock < quantity:
        messages.error(request, f"❌ Không đủ hàng! {product.name} chỉ còn {product.stock} sản phẩm.")
        return redirect('product_detail', id=product_id)

    order_item, created = Order.objects.get_or_create(
        user=request.user,
        product=product,
        status='cart',
        defaults={'quantity': quantity}
    )
    
    if not created:
        if product.stock < (order_item.quantity + quantity):
            messages.error(request, f"❌ Tổng số lượng trong giỏ ({order_item.quantity + quantity}) vượt quá tồn kho!")
        else:
            order_item.quantity += quantity
            order_item.save()
            messages.success(request, f"✅ Đã thêm {quantity} {product.name} vào giỏ hàng!")
    else:
        messages.success(request, f"✅ Đã thêm {product.name} vào giỏ hàng!")

    return redirect('view_cart')

@login_required
def update_cart_quantity(request, order_id, action):
    """Tăng/Giảm số lượng trực tiếp bằng nút bấm (+/-) trong giỏ hàng"""
    order_item = get_object_or_404(Order, id=order_id, user=request.user, status='cart')
    
    if action == 'increase':
        if order_item.product.stock > order_item.quantity:
            order_item.quantity += 1
            order_item.save()
        else:
            messages.warning(request, "⚠️ Số lượng trong kho đã đạt giới hạn!")
    elif action == 'decrease':
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()
            messages.info(request, "🗑️ Đã xóa sản phẩm khỏi giỏ hàng.")
            
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Order.objects.filter(user=request.user, status='cart')
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def my_orders(request):
    query = request.GET.get('q', '')
    orders_list = Order.objects.filter(user=request.user).exclude(status='cart').order_by('-id')
    
    if query:
        orders_list = orders_list.filter(product__name__icontains=query)
    
    paginator = Paginator(orders_list, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    return render(request, 'orders/my_orders.html', {'orders': orders, 'query': query})

@login_required
def checkout(request):
    """QUAN TRỌNG: Trừ kho thực tế + Gửi mail Hóa đơn HTML chi tiết ngầm"""
    cart_items = Order.objects.filter(user=request.user, status='cart')
    
    if not cart_items.exists():
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('view_cart')

    # Tính toán tổng tiền và kiểm tra kho
    total_bill = 0
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f"❌ Xin lỗi, {item.product.name} vừa hết hàng!")
            return redirect('view_cart')

    # Trừ kho và chốt trạng thái
    for item in cart_items:
        product = item.product
        product.stock -= item.quantity
        product.save()
        
        total_bill += product.price * item.quantity
        item.status = 'pending'
        item.save()
    
    # --- CHUẨN BỊ GỬI EMAIL HTML ---
    context = {
        'username': request.user.username,
        'order_id': request.user.id, # Dùng ID User làm mã đơn tạm thời
        'cart_items': cart_items,
        'total_bill': total_bill,
    }
    # Render file HTML thành chuỗi ký tự
    html_content = render_to_string('emails/order_receipt.html', context)
    subject = f"📦 Hóa đơn đơn hàng #{request.user.id} - Gift Shop"

    # Gửi mail HTML chạy ngầm
    threading.Thread(target=send_email_thread, args=(subject, html_content, [request.user.email])).start()

    messages.success(request, "🎉 Thanh toán thành công! Hóa đơn HTML đã được gửi về Mailtrap.")
    return redirect('my_orders')

# ==========================================
# PHẦN 2: DÀNH CHO ADMIN
# ==========================================

@staff_member_required
def admin_orders(request):
    query = request.GET.get('search', '')
    orders_list = Order.objects.all().order_by('-id')
    if query:
        orders_list = orders_list.filter(Q(product__name__icontains=query) | Q(user__username__icontains=query))
    paginator = Paginator(orders_list, 15)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    return render(request, 'orders/admin_order_list.html', {'orders': orders, 'query': query})

@staff_member_required
def update_order_status(request, id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=id)
        order.status = request.POST.get('status')
        order.save()
        messages.success(request, f"✅ Đã cập nhật trạng thái đơn hàng #{order.id}!")
    return redirect('admin_orders')

@login_required
def cancel_order(request, order_id):
    order_item = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
    product = order_item.product
    product.stock += order_item.quantity
    product.save()
    order_item.status = 'cancelled'
    order_item.save()
    messages.success(request, f"✅ Đã hủy đơn hàng #{order_item.id}. Sản phẩm đã hoàn lại kho.")
    return redirect('my_orders')

# ==========================================
# PHẦN 3: TƯƠNG TÁC (NEWSLETTER & FEEDBACK)
# ==========================================

def newsletter_signup(request):
    """Xử lý đăng ký nhận tin không gây lag trang web"""
    if request.method == "POST":
        email = request.POST.get('email')
        subject = '🎁 Chào mừng bạn đến với Gift Shop!'
        message = f'Cảm ơn {email} đã đăng ký nhận tin! Bạn sẽ nhận được các ưu đãi sớm nhất từ chúng tôi.'
        
        # Newsletter tạm thời dùng mail text đơn giản (hoặc có thể tạo template riêng sau)
        threading.Thread(target=send_mail, args=(subject, message, settings.DEFAULT_FROM_EMAIL, [email])).start()
        messages.success(request, "🎉 Đăng ký thành công! Hãy kiểm tra Mailtrap.")
        
    return redirect(request.META.get('HTTP_REFERER', '/'))

def submit_feedback(request):
    """Xử lý Kênh phản ánh (Khách gõ chữ gửi cho Admin)"""
    if request.method == "POST":
        email = request.POST.get('email')
        content = request.POST.get('message')
        
        subject = f"📢 PHẢN ÁNH MỚI TỪ: {email}"
        body = f"Nội dung lời nhắn của khách:\n\n{content}"
        
        # Gửi phản hồi về mail Admin
        threading.Thread(target=send_mail, args=(subject, body, settings.DEFAULT_FROM_EMAIL, ['admin@giftshop.com'])).start()
        
        messages.success(request, "🚀 Góp ý của bạn đã được gửi tới Ban quản trị. Cảm ơn Bạn Nhiều!")
        
    return redirect(request.META.get('HTTP_REFERER', '/'))