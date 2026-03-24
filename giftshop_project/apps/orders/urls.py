from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my/', views.my_orders, name='my_orders'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('manage/', views.admin_orders, name='admin_orders'),
    path('update-status/<int:id>/', views.update_order_status, name='update_order_status'),
]