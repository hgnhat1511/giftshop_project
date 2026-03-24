from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Address  # 🚀 Đã thêm import Address ở đây

# 1. ĐĂNG NHẬP
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') # Về thẳng trang chủ http://127.0.0.1:8000/
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")
    return render(request, "accounts/login.html")

# 2. ĐĂNG KÝ
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không đúng")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại")
            return redirect("register")

        # Tạo user mới
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Tạo profile đi kèm (Chỉ lưu full_name và phone)
        UserProfile.objects.create(user=user, full_name=full_name, phone=phone)
        
        messages.success(request, "Đăng ký thành công! Mời bạn đăng nhập.")
        return redirect("login")
    return render(request, "accounts/register.html")

# 3. ĐĂNG XUẤT
def logout_view(request):
    logout(request)
    return redirect('home')

# 4. TRANG CÁ NHÂN
@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.full_name = request.POST.get("full_name")
        profile.phone = request.POST.get("phone")
        profile.save()
        messages.success(request, "Cập nhật thông tin thành công")
        return redirect("profile")
    
    # 🚀 Lấy danh sách địa chỉ của User này từ Database
    user_addresses = Address.objects.filter(user=request.user).order_by('-id')

    # 🚀 Gửi biến addresses sang file HTML
    return render(request, "accounts/profile.html", {
        "profile": profile,
        "addresses": user_addresses
    })

# 5. THÊM ĐỊA CHỈ
@login_required
def add_address(request):
    if request.method == "POST":
        province = request.POST.get('province') # Đã sửa thành province cho khớp model
        district = request.POST.get('district')
        ward = request.POST.get('ward')
        detail = request.POST.get('detail')
        
        # 🚀 Lệnh lưu thẳng vào Database
        Address.objects.create(
            user=request.user,
            province=province,
            district=district,
            ward=ward,
            detail=detail
        )
        
        messages.success(request, "Đã thêm địa chỉ thành công!")
        
    return redirect('profile')

@login_required
def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    if request.method == "POST":
        address.province = request.POST.get('province')
        address.district = request.POST.get('district')
        address.ward = request.POST.get('ward')
        address.detail = request.POST.get('detail')
        address.save()
        messages.success(request, "Đã cập nhật địa chỉ!")
        return redirect('profile')
    return render(request, 'accounts/edit_address.html', {'address': address})

@login_required
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, "Đã xóa địa chỉ!")
    return redirect('profile')