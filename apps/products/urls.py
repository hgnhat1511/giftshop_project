from django.urls import path
from . import views

urlpatterns = [

    path('', views.product_list, name='product_list'),

    path('product/<int:id>/', views.product_detail, name='product_detail'),

    path('rating/<int:id>/', views.add_rating, name='add_rating'),

    # ADMIN PRODUCTS
    path('manage/', views.admin_products, name='admin_products'),
    
    path('add/', views.add_product, name='add_product'),
    
    path('edit/<int:id>/', views.edit_product, name='edit_product'),
    
    path('delete/<int:id>/', views.delete_product, name='delete_product'),

]