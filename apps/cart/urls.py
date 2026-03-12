from django.urls import path
from . import views

urlpatterns = [

    path("", views.cart_view, name="cart"),

    path("add/<int:id>/", views.add_to_cart, name="add_to_cart"),

    path("decrease/<int:id>/", views.decrease_cart, name="decrease_cart"),

    path("remove/<int:id>/", views.remove_cart, name="remove_cart"),

]