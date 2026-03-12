from django.shortcuts import render
from apps.products.models import Product
from apps.cart.models import Cart

def dashboard_view(request):

    product_count = Product.objects.count()

    cart_count = Cart.objects.count()

    return render(request,"dashboard/dashboard.html",
    {
        "product_count":product_count,
        "cart_count":cart_count
    })