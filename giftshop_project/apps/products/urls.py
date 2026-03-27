from django.urls import path
from . import views

urlpatterns = [
    # BỎ DÒNG TRANG CHỦ RỖNG Ở ĐÂY ĐỂ TRÁNH VÒNG LẶP VỚI FILE TỔNG
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('rating/<int:id>/', views.add_rating, name='add_rating'),
    
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),

    path('stores/', views.store_map_view, name='store_list'),
    path('api/stores/', views.api_store_list, name='api_stores'),

    # Admin Products
    path('manage/', views.admin_products, name='admin_products'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:id>/', views.edit_product, name='edit_product'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),

    # Admin Stores
    path('admin/stores/', views.admin_stores, name='admin_store_list'),
    path('admin/stores/add/', views.add_store, name='add_store'),
    path('admin/stores/edit/<int:id>/', views.edit_store, name='edit_store'),
    path('admin/stores/delete/<int:id>/', views.delete_store, name='delete_store'),
]