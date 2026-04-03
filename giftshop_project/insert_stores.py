import os
import django
import random

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giftshop_project.settings')
django.setup()

# LƯU Ý: Nếu bảng Store của bạn nằm ở app khác (VD: apps.stores.models) thì nhớ sửa lại dòng này nhé!
from apps.products.models import Store

def run():
    print("Đang xóa dữ liệu cũ...")
    Store.objects.all().delete()
    
    print("Đang nạp 50 chi nhánh quanh TP.HCM...")
    for i in range(1, 51): # Để range tới 51 thì nó mới nạp đủ 50 cái (từ 1 đến 50)
        # CHỮ S ĐÃ ĐƯỢC VIẾT HOA VÀ THỤT LỀ CHUẨN
        Store.objects.create(
            name=f"Gift Shop Chi nhánh {i}",
            address=f"Số {i} Đường số {random.randint(1,50)}, TP.HCM",
            lat=10.75 + random.uniform(-0.05, 0.05),
            lng=106.67 + random.uniform(-0.05, 0.05),
            phone=f"090{random.randint(1000000, 9999999)}",
            revenue=random.randint(5000000, 50000000) # Doanh thu từ 5tr - 50tr
        )
        
    print("--- THÀNH CÔNG! Đã có 50 chi nhánh trong Database ---")

if __name__ == '__main__':
    run()