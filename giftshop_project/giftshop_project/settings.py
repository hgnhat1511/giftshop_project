from pathlib import Path
import os


# Đường dẫn gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# BẢO MẬT
SECRET_KEY = 'django-insecure-your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

# --- CẤU HÌNH CÁC APP ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'anymail',

    # Các App nội bộ của Nhật
    'apps.accounts',
    'apps.products',
    'apps.orders',
    'apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'giftshop_project.urls'

# --- CẤU HÌNH GIAO DIỆN (TEMPLATES) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Nơi chứa các file HTML dùng chung như base.html, navbar.html
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'giftshop_project.wsgi.application'

# --- CƠ SỞ DỮ LIỆU ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- CẤU HÌNH ĐĂNG NHẬP / ĐIỀU HƯỚNG ---
# Giúp sửa lỗi đăng nhập xong bị nhảy lung tung
LOGIN_REDIRECT_URL = '/'      # Đăng nhập xong về trang chủ
LOGOUT_REDIRECT_URL = '/'     # Đăng xuất xong về trang chủ
LOGIN_URL = '/accounts/login/' # Trang đăng nhập mặc định

# Ngôn ngữ và Múi giờ
LANGUAGE_CODE = 'vi'           # Đổi sang tiếng Việt cho giao diện Admin
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# --- CẤU HÌNH FILE TĨNH (CSS, JS, IMAGES) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- CẤU HÌNH MEDIA (ẢNH SẢN PHẨM) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# settings.py
ANYMAIL = {
    "MAILTRAP_API_TOKEN": "c52f6f866bc4e642ee2cd9e21e7139b6",
    "MAILTRAP_SANDBOX_ID": 4508788,
}
EMAIL_BACKEND = "anymail.backends.mailtrap.EmailBackend"

# Đừng quên dòng này để mail hiện tên shop cho đẹp nhé
DEFAULT_FROM_EMAIL = "Gift Shop <noreply@giftshop.com>"