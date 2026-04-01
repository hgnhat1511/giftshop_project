import os
import django

# 1. Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giftshop_project.settings')
django.setup()

# 2. Import model Product (LƯU Ý: Nếu model Product của bạn nằm ở thư mục khác thì sửa lại đoạn này nhé)
from apps.products.models import Product

def run():
    print("Đang dọn dẹp kho hàng cũ...")
    Product.objects.all().delete()
    
    print("Đang nhập lô hàng quà tặng xịn xò mới...")
    
    # Danh sách 15 món quà tặng chuẩn E-commerce
    products_data = [
        {"name": "Gấu bông Teddy khổng lồ 1m2", "price": 450000, "desc": "Chất liệu nỉ nhung cao cấp, mềm mịn, an toàn cho da."},
        {"name": "Hộp âm nhạc pha lê 3D", "price": 250000, "desc": "Phát sáng lấp lánh, bản nhạc Fur Elise du dương."},
        {"name": "Set nến thơm thư giãn", "price": 150000, "desc": "Chiết xuất tinh dầu thiên nhiên, giúp giảm stress hiệu quả."},
        {"name": "Bó hoa hồng sáp thơm 99 bông", "price": 350000, "desc": "Hoa vĩnh cửu không tàn, biểu tượng tình yêu vĩnh cửu."},
        {"name": "Sổ tay da thật Vintage", "price": 120000, "desc": "Bìa da thật phong cách cổ điển, giấy kraft chống lóa."},
        {"name": "Set cốc sứ đôi Cute", "price": 180000, "desc": "Sứ tráng men cao cấp, in hình nặn nổi siêu dễ thương."},
        {"name": "Đèn ngủ mặt trăng 3D", "price": 220000, "desc": "Đổi 16 màu bằng điều khiển cảm ứng, có pin sạc tiện lợi."},
        {"name": "Khung ảnh gỗ Decor bàn làm việc", "price": 90000, "desc": "Khung gỗ sồi tự nhiên, kèm mặt kính mica trong suốt."},
        {"name": "Móc khóa len Handmade hình thú", "price": 45000, "desc": "Đan tay 100% tỉ mỉ, nhiều mẫu mã đa dạng."},
        {"name": "Hộp son môi cao cấp kèm thiệp", "price": 650000, "desc": "Set quà tặng sang trọng dành cho phái đẹp."},
        {"name": "Nước hoa Mini chính hãng", "price": 350000, "desc": "Lưu hương lâu tới 8h, thiết kế chai nhỏ gọn tinh tế."},
        {"name": "Lọ hoa thủy tinh Decor", "price": 280000, "desc": "Kiểu dáng Bắc Âu thanh lịch, phù hợp cắm nhiều loại hoa."},
        {"name": "Túi Tote vải Canvas", "price": 110000, "desc": "Dày dặn, in hình theo yêu cầu, vừa A4 và Laptop 13 inch."},
        {"name": "Bút ký doanh nhân mạ vàng", "price": 400000, "desc": "Ngòi trơn, mực đều, kèm hộp nhung sang trọng."},
        {"name": "Hộp quà bí mật (Mystery Box)", "price": 500000, "desc": "Bên trong chứa ngẫu nhiên 3-5 món đồ giá trị cao."}
    ]

    for item in products_data:
        # ⚠️ CHÚ Ý: Nếu các cột trong Models của bạn tên khác (VD: 'title' thay vì 'name', hoặc 'chi_tiet' thay vì 'description') 
        # thì bạn sửa lại các chữ màu trắng ở bên trái dấu = cho đúng với code của bạn nhé!
        Product.objects.create(
            name=item["name"],
            price=item["price"],
            description=item["desc"]
        )
        
    print(f"--- THÀNH CÔNG! Đã nạp đầy kho với {len(products_data)} sản phẩm mới ---")

if __name__ == '__main__':
    run()
    
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