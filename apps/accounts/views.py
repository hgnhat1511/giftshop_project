from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserProfile


# LOGIN
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            next_url = request.GET.get("next", "/")

            return redirect(next_url)

        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")

    return render(request, "accounts/login.html")


# REGISTER
def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # kiểm tra username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại")
            return redirect("register")

        # kiểm tra email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng")
            return redirect("register")

        # tạo user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # tạo profile
        UserProfile.objects.create(user=user)

        messages.success(request, "Đăng ký thành công")

        return redirect("login")

    return render(request, "accounts/register.html")


# LOGOUT
def logout_view(request):

    logout(request)

    return redirect("/")


# PROFILE
@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.full_name = request.POST.get("full_name")
        profile.phone = request.POST.get("phone")

        profile.province = request.POST.get("province")
        profile.district = request.POST.get("district")
        profile.ward = request.POST.get("ward")
        profile.detail_address = request.POST.get("detail_address")

        profile.save()

        messages.success(request, "Cập nhật thông tin thành công")

        return redirect("profile")

    return render(request, "accounts/profile.html", {
        "profile": profile
    })


# ADD ADDRESS
@login_required
def add_address(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.province = request.POST.get("province")
        profile.district = request.POST.get("district")
        profile.ward = request.POST.get("ward")
        profile.detail_address = request.POST.get("detail_address")

        profile.save()

        messages.success(request, "Thêm địa chỉ thành công")

        return redirect("profile")

    return render(request, "accounts/add_address.html")