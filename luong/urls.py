from django.urls import path
from .views import  xem_bang_luong_cua_nhan_vien, xem_bang_luong_cua_toi, danh_sach_nhan_vien_va_luong, chuyen_huong_luong
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Dành cho nhân viên bình thường xem bảng lương của chính họ
    path('luong-cua-toi/', xem_bang_luong_cua_toi, name='xem_bang_luong_cua_toi'),
    path('luong/', chuyen_huong_luong, name='chuyen_huong_luong'),
    # Dành cho kế toán xem danh sách nhân viên
    path('danh-sach-nhan-vien/', danh_sach_nhan_vien_va_luong, name='danh_sach_nhan_vien'),

    # Dành cho kế toán xem bảng lương của từng nhân viên
    path('luong-nhan-vien/<int:nhan_vien_id>/', xem_bang_luong_cua_nhan_vien, name='xem_bang_luong_cua_nhan_vien'),
]