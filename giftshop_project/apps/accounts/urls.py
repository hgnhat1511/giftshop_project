from django.urls import path
from .views import (
    login_view,
    register_view,
    logout_view,
    profile_view,
    add_address
)

urlpatterns = [

    # đăng nhập
    path("login/", login_view, name="login"),

    # đăng ký
    path("register/", register_view, name="register"),

    # đăng xuất
    path("logout/", logout_view, name="logout"),

    # trang thông tin tài khoản
    path("profile/", profile_view, name="profile"),

    # thêm địa chỉ
    path("address/add/", add_address, name="add_address"),

]

# Da update them moi (test)