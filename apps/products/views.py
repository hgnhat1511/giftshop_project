from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Product, Rating
from django.contrib.admin.views.decorators import staff_member_required



# =============================
# Trang bán hàng (Trang chủ)
# =============================

def product_list(request):

    products = Product.objects.all()

    # search
    q = request.GET.get("q")

    if q:
        products = products.filter(name__icontains=q)

    # pagination
    paginator = Paginator(products, 8)

    page = request.GET.get("page")

    products = paginator.get_page(page)

    return render(request, "products/product_list.html", {
        "products": products,
        "q": q
    })


# =============================
# Chi tiết sản phẩm
# =============================

def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    return render(request, "products/product_detail.html", {
        "product": product
    })


# =============================
# Thêm rating
# =============================

def add_rating(request, id):

    product = get_object_or_404(Product, id=id)

    stars = request.POST["stars"]

    Rating.objects.create(
        product=product,
        user=request.user,
        stars=stars
    )

    return redirect("/product/" + str(id))


# =============================
# Trang quản lý sản phẩm
# =============================

def admin_products(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request,
        'products/admin_product_list.html',
        {'products': products}
    )

# =============================
# Thêm sản phẩm
# =============================

def add_product(request):

    if request.method == "POST":

        name = request.POST["name"]
        price = request.POST["price"]
        stock = request.POST.get("stock")
        description = request.POST["description"]
        image = request.FILES.get("image")

        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description,
            image=image
        )

        return redirect("/products/manage/")

    return render(request, "products/add_product.html")


# =============================
# Sửa sản phẩm
# =============================

def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.description = request.POST.get("description")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        return redirect("admin_products")

    return render(request,"products/edit_product.html",{
        "product":product
    })


# =============================
# Xóa sản phẩm
# =============================

def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect("admin_products")

    return render(request, "products/delete_product.html", {
        "product": product
    })

@staff_member_required
def admin_products(request):

    products = Product.objects.all()

    return render(
        request,
        "products/admin_product_list.html",
        {"products": products}
    )