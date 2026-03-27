from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Product, Rating, Store
from apps.orders.models import Order
from django.db.models import Q

# ==========================================
# PHẦN 1: WEBGIS & QUẢN LÝ CỬA HÀNG
# ==========================================

def store_map_view(request):
    """Trang hiển thị bản đồ 101 chi nhánh cho KHÁCH"""
    return render(request, 'products/store_map.html')

def api_store_list(request):
    """API trả về dữ liệu cho Leaflet"""
    stores = list(Store.objects.values('id', 'name', 'address', 'lat', 'lng', 'phone', 'revenue'))
    return JsonResponse(stores, safe=False)

@staff_member_required
def admin_stores(request):
    """Trang danh sách cửa hàng dạng bảng cho ADMIN sửa/xóa + Tìm kiếm"""
    # 1. Lấy từ khóa từ ô tìm kiếm (name="search")
    query = request.GET.get('search', '')

    # 2. Lọc dữ liệu
    if query:
        stores = Store.objects.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query)
        ).order_by('-id')
    else:
        stores = Store.objects.all().order_by('-id')
        
    # 3. Trả về kết quả kèm từ khóa để hiển thị lại trên ô nhập
    return render(request, 'products/admin_store_list.html', {
        'stores': stores,
        'query': query
    })

# 🚀 ĐÃ BỔ SUNG HÀM THÊM CỬA HÀNG
def add_store(request):
    if request.method == "POST":
        Store.objects.create(
            name=request.POST.get("name"),
            address=request.POST.get("address"),
            lat=request.POST.get("lat", 0),
            lng=request.POST.get("lng", 0),
            phone=request.POST.get("phone"),
            store_type=request.POST.get("store_type", "Gift Shop"),
            revenue=request.POST.get("revenue", 0)
        )
        messages.success(request, "Đã thêm cửa hàng mới thành công!")
        return redirect("admin_store_list")
    return render(request, "products/add_store.html")

def edit_store(request, id):
    """Sửa thông tin chi nhánh (Bổ sung đầy đủ các trường)"""
    store = get_object_or_404(Store, id=id)
    if request.method == "POST":
        store.name = request.POST.get("name")
        store.address = request.POST.get("address") # Đã thêm
        store.phone = request.POST.get("phone")     # Đã thêm
        store.store_type = request.POST.get("store_type") # Đã thêm
        store.lat = request.POST.get("lat")
        store.lng = request.POST.get("lng")
        store.revenue = request.POST.get("revenue")
        store.save()
        messages.success(request, "Đã cập nhật thông tin cửa hàng!")
        return redirect('admin_store_list')
    return render(request, "products/edit_store.html", {"store": store})

def delete_store(request, id):
    store = get_object_or_404(Store, id=id)
    # Cải tiến: Nếu dùng nút bấm xóa trực tiếp không cần form xác nhận thì bỏ if request.method == 'POST'
    store.delete()
    messages.success(request, "Đã xóa cửa hàng!")
    return redirect('admin_store_list')


# ==========================================
# PHẦN 2: BÁN HÀNG & GIỎ HÀNG
# ==========================================

def product_list(request):
    products = Product.objects.all()
    q = request.GET.get("q")
    if q: products = products.filter(name__icontains=q)
    
    paginator = Paginator(products, 8)
    page = request.GET.get("page")
    products = paginator.get_page(page)
    return render(request, "products/product_list.html", {"products": products, "q": q})

def add_to_cart(request, id):
    if not request.user.is_authenticated: return redirect('login')
    product = get_object_or_404(Product, id=id)
    Order.objects.create(user=request.user, product=product, quantity=1, status='pending')
    messages.success(request, f"Đã thêm {product.name} vào đơn hàng!")
    return redirect('/orders/my/') 

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "products/product_detail.html", {"product": product})

def add_rating(request, id):
    product = get_object_or_404(Product, id=id)
    stars = request.POST.get("stars")
    if stars: Rating.objects.create(product=product, user=request.user, stars=stars)
    return redirect("/product/" + str(id))

# ==========================================
# PHẦN 3: QUẢN LÝ SẢN PHẨM (ADMIN)
# ==========================================

@staff_member_required
def admin_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all().order_by('-id')
    return render(request, 'products/admin_product_list.html', {'products': products})

def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get("name"), 
            price=request.POST.get("price", 0),
            stock=request.POST.get("stock", 0), 
            description=request.POST.get("description"),
            image=request.FILES.get("image")
        )
        messages.success(request, "Đã thêm sản phẩm thành công!")
        return redirect("admin_products")
    return render(request, "products/add_product.html")

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")             # Đã thêm
        product.description = request.POST.get("description") # Đã thêm
        
        # Chỉ cập nhật ảnh nếu người dùng có chọn ảnh mới
        if request.FILES.get("image"):
            product.image = request.FILES.get("image")
            
        product.save()
        messages.success(request, "Đã cập nhật sản phẩm thành công!")
        return redirect("admin_products")
    return render(request, "products/edit_product.html", {"product": product})

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Đã xóa sản phẩm!")
    return redirect("admin_products")