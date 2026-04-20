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
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import threading
import pandas as pd
from django.http import HttpResponse
from apps.accounts.models import Address
from apps.products.models import Category

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
    """QUAN TRỌNG: Xử lý 3 loại địa chỉ + Trừ kho thực tế + Gửi mail Hóa đơn"""
    cart_items = Order.objects.filter(user=request.user, status='cart')
    
    if not cart_items.exists():
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('view_cart')

    # Tính toán tổng tiền
    total_bill = sum(item.product.price * item.quantity for item in cart_items)

    # 1. XỬ LÝ KHI NGƯỜI DÙNG BẤM "THANH TOÁN" (GỬI FORM 3 TABS)
    if request.method == "POST":
        addr_mode = request.POST.get('addr_mode')
        shipping_address = ""

        # Lọc ra địa chỉ giao hàng cuối cùng dựa theo Tab được chọn
        if addr_mode == 'saved':
            address_id = request.POST.get('address_id')
            if address_id:
                addr_obj = get_object_or_404(Address, id=address_id, user=request.user)
                shipping_address = f"{addr_obj.detail}, {addr_obj.ward}, {addr_obj.district}, {addr_obj.province}"
            else:
                messages.error(request, "Vui lòng chọn địa chỉ đã lưu!")
                return redirect('checkout')
                
        elif addr_mode == 'manual':
            shipping_address = request.POST.get('manual_address', 'Khách nhập tay không ghi rõ')
            
        elif addr_mode == 'map':
            lat = request.POST.get('lat', '')
            lng = request.POST.get('lng', '')
            # Lấy chuỗi chữ địa chỉ từ hidden input (bạn có thể thêm input name="map_address_text" ở HTML)
            map_text = request.POST.get('map_address_text', '') 
            shipping_address = f"{map_text} (Tọa độ: {lat}, {lng})"

        # Giữ nguyên code kiểm tra kho của bạn
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(request, f"❌ Xin lỗi, {item.product.name} vừa hết hàng!")
                return redirect('view_cart')

        # Giữ nguyên code trừ kho và chốt trạng thái của bạn
        for item in cart_items:
            product = item.product
            product.stock -= item.quantity
            product.save()
            
            item.status = 'pending'
            # Nếu Model Order của bạn có trường ghi chú/địa chỉ thì lưu vào đây:
            # item.shipping_address = shipping_address 
            item.save()
        
        # --- CHUẨN BỊ GỬI EMAIL HTML ---
        context = {
            'username': request.user.username,
            'order_id': request.user.id, # Dùng ID User làm mã đơn tạm thời
            'cart_items': cart_items,
            'total_bill': total_bill,
            'shipping_address': shipping_address, # Gửi kèm địa chỉ vào mail cho xịn
        }
        html_content = render_to_string('emails/order_receipt.html', context)
        subject = f"📦 Hóa đơn đơn hàng #{request.user.id} - Gift Shop"

        threading.Thread(target=send_email_thread, args=(subject, html_content, [request.user.email])).start()

        messages.success(request, f"🎉 Đặt hàng thành công! Đơn sẽ giao đến: {shipping_address}")
        return redirect('my_orders')

    # 2. XỬ LÝ KHI VÀO TRANG MỞ GIAO DIỆN CHỌN ĐỊA CHỈ (GET)
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'orders/checkout.html', {
        'addresses': addresses,
        'cart_items': cart_items,
        'total_bill': total_bill
    })

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
        new_status = request.POST.get('status')
        
        # Chỉ xử lý nếu trạng thái thực sự thay đổi
        if order.status != new_status:
            order.status = new_status
            order.save()
            
            # Từ điển dịch mã trạng thái siêu ngắn gọn
            status_dict = {
                'pending': 'Chờ xử lý',
                'shipping': 'Đang giao',
                'completed': 'Hoàn thành',
                'delivered': 'Hoàn thành',
                'cancelled': 'Hủy'
            }
            readable_status = status_dict.get(new_status, new_status)
            
            # Tiêu đề và nội dung mail đánh nhanh rút gọn
            subject = f"Thông báo đơn hàng #{order.id}"
            message = f"Đơn hàng #{order.id} của bạn đã được: {readable_status}."
            
            # Gửi mail NGẦM (Chỉ gửi nếu tài khoản có email)
            if order.user.email:
                threading.Thread(
                    target=send_mail, 
                    args=(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
                ).start()
                messages.success(request, f"✅ Đã cập nhật đơn hàng #{order.id} thành: {readable_status} (Đã báo mail)!")
            else:
                messages.success(request, f"✅ Đã cập nhật đơn hàng #{order.id} thành: {readable_status} (Khách chưa có email)!")
        else:
            messages.info(request, f"ℹ️ Trạng thái không thay đổi.")
            
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

# ==========================================
# PHẦN 4: NHẬP & XUẤT EXCEL (IMPORT/EXPORT)
# ==========================================

@staff_member_required
def export_orders_excel(request):
    """Xuất toàn bộ danh sách đơn hàng ra file Excel"""
    # Lấy dữ liệu từ Database
    orders = Order.objects.all().values(
        'id', 'user__username', 'product__name', 'quantity', 'status'
    )
    
    # Chuyển thành DataFrame của Pandas
    df = pd.DataFrame(list(orders))
    
    # Đổi tên cột tiếng Việt cho file Excel
    if not df.empty:
        df.columns = ['Mã Đơn', 'Tên Khách Hàng', 'Sản Phẩm', 'Số Lượng', 'Trạng Thái']
    
    # Trả về response dạng file tải xuống
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Danh_sach_don_hang.xlsx"'
    
    # Ghi dữ liệu vào file
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

@staff_member_required
def import_products_excel(request):
    """Nhập danh sách sản phẩm từ file Excel"""
    if request.method == "POST" and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        try:
            # Đọc file Excel
            df = pd.read_excel(excel_file)
            
            # Tự động gọt bỏ mọi khoảng trắng dư thừa ở tên cột
            df.columns = df.columns.str.strip()
            
            # Lặp qua từng dòng để lưu vào Database
            for index, row in df.iterrows():
                
                # --- PHẦN 1: XỬ LÝ DANH MỤC TỰ ĐỘNG ---
                cat_name = row.get('Danh Mục', '')
                category_obj = None
                
                # Nếu file Excel có nhập cột Danh Mục (không bị trống)
                if cat_name and str(cat_name) != 'nan':
                    # Lệnh này sẽ tìm danh mục, nếu chưa có nó tự tạo cái mới luôn!
                    category_obj, created = Category.objects.get_or_create(name=str(cat_name).strip())

                # --- PHẦN 2: LƯU SẢN PHẨM KHỚP VỚI CỘT EXCEL ---
                Product.objects.create(
                    name=row.get('Tên Sản Phẩm', 'Sản phẩm chưa đặt tên'), # Chữ hoa y như file Excel
                    price=row.get('Giá Bán', 0),                           # Cột Giá Bán
                    stock=row.get('Số Lượng Tồn', 0),                      # Cột Số Lượng Tồn
                    category=category_obj                                  # Gắn danh mục tự động
                )
                
            messages.success(request, f"✅ Đã nhập thành công {len(df)} sản phẩm từ Excel!")
        except Exception as e:
            messages.error(request, f"❌ Lỗi khi đọc file Excel: Vui lòng kiểm tra lại tên cột. Chi tiết: {e}")
            
    # Load lại trang danh sách sản phẩm của Admin
    return redirect(request.META.get('HTTP_REFERER', '/'))