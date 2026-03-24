from django.contrib import admin
from django.urls import path, include
from apps.products.views import product_list 
# Thêm 2 thư viện này để load ảnh
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🏠 TRANG CHỦ: Trỏ thẳng vào hàm xử lý, KHÔNG dùng include ở đây
    path('', product_list, name='home'), 

    # Các App con: Đặt tiền tố rõ ràng để không bị trùng
    path('products/', include('apps.products.urls')), 
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

# Thêm đoạn này vào dưới cùng để Django hiển thị được ảnh tĩnh (Media)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)