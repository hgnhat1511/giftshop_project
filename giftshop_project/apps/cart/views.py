from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Cart
from apps.products.models import Product


# HIỂN THỊ GIỎ HÀNG
@login_required
def cart_view(request):

    items = Cart.objects.filter(user=request.user)

    total = 0

    for item in items:
        total += item.product.price * item.quantity

    return render(
        request,
        "cart/cart.html",
        {
            "items": items,
            "total": total
        }
    )


# THÊM VÀO GIỎ
@login_required
def add_to_cart(request, id):

    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("/cart/")


# GIẢM SỐ LƯỢNG
@login_required
def decrease_cart(request, id):

    cart_item = get_object_or_404(
        Cart,
        user=request.user,
        product_id=id
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("/cart/")


# XÓA SẢN PHẨM KHỎI GIỎ
@login_required
def remove_cart(request, id):

    cart_item = get_object_or_404(
        Cart,
        user=request.user,
        product_id=id
    )

    cart_item.delete()

    return redirect("/cart/")