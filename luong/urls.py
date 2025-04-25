from django.urls import path
from .views import danh_sach_luong
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('tinh_luong/', danh_sach_luong, name='tinh_luong_hang_thang'),
]