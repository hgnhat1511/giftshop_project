from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Product, Rating, Store, Category,ProductImage
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
    """Trang danh sách cửa hàng dạng bảng cho ADMIN sửa/xóa + Tìm kiếm + Phân trang"""
    query = request.GET.get('search', '')

    # Lọc dữ liệu
    if query:
        stores_list = Store.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        ).order_by('-id')
    else:
        stores_list = Store.objects.all().order_by('-id')
        
    # Phân trang (10 cửa hàng/trang)
    paginator = Paginator(stores_list, 10)
    page = request.GET.get('page')
    stores = paginator.get_page(page) 
        
    return render(request, 'products/admin_store_list.html', {
        'stores': stores,
        'query': query
    })

def add_store(request):
    if request.method == "POST":
        try:
            lat = float(request.POST.get("lat", 0))
            lng = float(request.POST.get("lng", 0))
            revenue = int(request.POST.get("revenue", 0))
        except ValueError:
            messages.error(request, "❌ Lỗi: Tọa độ và doanh thu phải là số!")
            return redirect("add_store")

        if lat < -90 or lat > 90:
            messages.error(request, "❌ Lỗi: Vĩ độ (Lat) bắt buộc phải từ -90 đến 90!")
            return redirect("add_store")

        if lng < -180 or lng > 180:
            messages.error(request, "❌ Lỗi: Kinh độ (Lng) bắt buộc phải từ -180 đến 180!")
            return redirect("add_store")

        if revenue < 0:
            messages.error(request, "❌ Lỗi: Doanh thu không được là số âm!")
            return redirect("add_store")

        Store.objects.create(
            name=request.POST.get("name"),
            address=request.POST.get("address"),
            lat=lat,
            lng=lng,
            phone=request.POST.get("phone"),
            store_type=request.POST.get("store_type", "Gift Shop"),
            revenue=revenue
        )
        
        messages.success(request, "Đã thêm cửa hàng mới thành công!")
        return redirect("admin_store_list")
        
    return render(request, "products/add_store.html")

def edit_store(request, id):
    store = get_object_or_404(Store, id=id)
    if request.method == "POST":
        try:
            revenue = int(request.POST.get("revenue", store.revenue))
        except ValueError:
            messages.error(request, "❌ Lỗi: Doanh thu phải là số hợp lệ!")
            return redirect('edit_store', id=id)

        if revenue < 0:
            messages.error(request, "❌ Lỗi: Doanh thu không được là số âm!")
            return redirect('edit_store', id=id)

        store.name = request.POST.get("name")
        store.address = request.POST.get("address")
        store.phone = request.POST.get("phone")
        store.store_type = request.POST.get("store_type")
        store.lat = request.POST.get("lat")
        store.lng = request.POST.get("lng")
        store.revenue = revenue
        store.save()
        messages.success(request, "Đã cập nhật thông tin cửa hàng!")
        return redirect('admin_store_list')
    return render(request, "products/edit_store.html", {"store": store})

def delete_store(request, id):
    store = get_object_or_404(Store, id=id)
    store.delete()
    messages.success(request, "Đã xóa cửa hàng!")
    return redirect('admin_store_list')


# ==========================================
# PHẦN 2: BÁN HÀNG & GIỎ HÀNG
# ==========================================

def product_list(request):
    """Danh sách sản phẩm cho Khách + Lọc Danh Mục + Lọc giá + Tìm kiếm"""
    q = request.GET.get("q", "")
    sort_by = request.GET.get("sort_by", "") 
    category_slug = request.GET.get('category', '') # <== 1. LẤY DANH MỤC KHÁCH CHỌN
    
    # 2. Lấy danh sách category để hiện lên thanh menu
    categories = Category.objects.all()
    
    # Bắt đầu với toàn bộ sản phẩm
    products_list = Product.objects.all()
    
    # 3. Lọc theo Category nếu có
    if category_slug:
        products_list = products_list.filter(category__slug=category_slug)
    
    # Tìm kiếm theo tên (nếu có gõ chữ)
    if q:
        products_list = products_list.filter(name__icontains=q)
        
    # Lọc và Sắp xếp theo giá
    if sort_by == 'asc':
        products_list = products_list.order_by('price') 
    elif sort_by == 'desc':
        products_list = products_list.order_by('-price') 
    else:
        products_list = products_list.order_by('-id') 
    
    # Phân trang (8 sản phẩm/trang)
    paginator = Paginator(products_list, 8)
    page = request.GET.get("page")
    products = paginator.get_page(page) 
    
    return render(request, "products/product_list.html", {
        "products": products,
        "categories": categories, # <== Truyền danh mục ra html
        "category_slug": category_slug, # <== Giữ trạng thái nút bấm
        "q": q,
        "sort_by": sort_by
    })

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
    """Trang quản lý sản phẩm ADMIN + Lọc Danh Mục + Phân trang"""
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', '') 
    category_id = request.GET.get('category_id', '') # <== Lọc theo ID danh mục bên Admin

    # Bắt đầu với danh sách gốc
    products_list = Product.objects.all()
    categories = Category.objects.all() # Lấy danh mục cho Admin chọn
    
    # Lọc theo Category trong Admin
    if category_id:
        products_list = products_list.filter(category_id=category_id)

    # Lọc theo tên (Search)
    if query:
        products_list = products_list.filter(name__icontains=query)

    # Lọc theo giá (Sort)
    if sort_by == 'asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'desc':
        products_list = products_list.order_by('-price')
    else:
        products_list = products_list.order_by('-id') 
        
    # Phân trang (10 sản phẩm/trang)
    paginator = Paginator(products_list, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'products/admin_product_list.html', {
        'products': products,
        'categories': categories, # Truyền ra HTML
        'category_id': category_id,
        'query': query,
        'sort_by': sort_by 
    })

def add_product(request):
    if request.method == "POST":
        # Tìm category dựa vào id gửi lên từ form
        category_id = request.POST.get("category_id")
        category = Category.objects.filter(id=category_id).first() if category_id else None

        # 1. Lưu sản phẩm chính trước
        new_product = Product.objects.create(
            name=request.POST.get("name"),
            category=category, 
            price=request.POST.get("price", 0),
            stock=request.POST.get("stock", 0),
            description=request.POST.get("description"),
            image=request.FILES.get("image") # Đây là ảnh chính
        )
        
        # ==========================================
        # 2. XỬ LÝ UPLOAD NHIỀU ẢNH PHỤ (GALLERY)
        # ==========================================
        # Lấy danh sách tất cả các file ảnh có tên là 'gallery' từ form
        gallery_images = request.FILES.getlist('gallery')
        
        # Vòng lặp lưu từng ảnh vào bảng ProductImage
        for img in gallery_images:
            ProductImage.objects.create(product=new_product, image=img)
        # ==========================================

        messages.success(request, "Đã thêm sản phẩm và ảnh phụ thành công!")
        return redirect("admin_products")
    
    categories = Category.objects.all()
    return render(request, "products/add_product.html", {"categories": categories})

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        category = Category.objects.filter(id=category_id).first() if category_id else None

        # 1. Cập nhật thông tin sản phẩm chính
        product.name = request.POST.get("name")
        product.category = category 
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.description = request.POST.get("description")
        
        if request.FILES.get("image"):
            product.image = request.FILES.get("image")
            
        product.save()
        
        # ==========================================
        # 2. XÓA ẢNH PHỤ NẾU NGƯỜI DÙNG TÍCH CHỌN
        # ==========================================
        # Lấy danh sách các ID ảnh mà người dùng đã tích vào ô Xóa
        delete_image_ids = request.POST.getlist('delete_images')
        if delete_image_ids:
            # Lệnh filter(id__in=...) giúp tìm và xóa nhiều ảnh cùng 1 lúc cực nhanh
            ProductImage.objects.filter(id__in=delete_image_ids).delete()
        
        # ==========================================
        # 3. UPLOAD THÊM ẢNH PHỤ MỚI (NẾU CÓ)
        # ==========================================
        gallery_images = request.FILES.getlist('gallery')
        for img in gallery_images:
            ProductImage.objects.create(product=product, image=img)
        # ==========================================

        messages.success(request, "Đã cập nhật sản phẩm thành công!")
        return redirect("admin_products")
        
    categories = Category.objects.all()
    return render(request, "products/edit_product.html", {"product": product, "categories": categories})

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Đã xóa sản phẩm!")
    return redirect("admin_products")

# ==========================================
# PHẦN 4: QUẢN LÝ DANH MỤC (CATEGORY)
# ==========================================

@staff_member_required
def admin_categories(request):
    """Trang danh sách Danh mục cho Admin"""
    categories = Category.objects.all().order_by('-id')
    return render(request, 'products/admin_category_list.html', {'categories': categories})

@staff_member_required
def add_category(request):
    """Trang thêm Danh mục"""
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            messages.success(request, "Đã thêm danh mục thành công!")
            return redirect('admin_categories')
    return render(request, 'products/add_category.html')

@staff_member_required
def edit_category(request, id):
    """Trang sửa Danh mục"""
    category = get_object_or_404(Category, id=id)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            category.name = name
            category.save()
            messages.success(request, "Đã cập nhật danh mục thành công!")
            return redirect('admin_categories')
    return render(request, 'products/add_category.html', {'category': category})

@staff_member_required
def delete_category(request, id):
    """Xóa Danh mục"""
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, "Đã xóa danh mục!")
    return redirect('admin_categories')