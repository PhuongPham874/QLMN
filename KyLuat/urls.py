from django.urls import path
from .views import ky_luat_list, add_ky_luat, xoa_ky_luat, ky_luat_cua_toi, edit_ky_luat, duyet_ky_luat, ky_luat_cho_duyet, ky_luat_khen_thuong

urlpatterns = [
    path('ky-luat/', ky_luat_list, name='ky_luat_list'),
    path('ky-luat/add/', add_ky_luat, name='add_ky_luat'),
    path('ky-luat/xoa/<int:ky_luat_id>/', xoa_ky_luat, name='xoa_ky_luat'),
    path('ky-luat-cua-toi/', ky_luat_cua_toi, name='ky_luat_cua_toi'),
    path('ky-luat/edit/<int:ky_luat_id>/', edit_ky_luat, name='edit_ky_luat'),
    path('ky-luat/duyet/<int:ky_luat_id>/', duyet_ky_luat, name='duyet_ky_luat'),
    path('ky-luat/cho-duyet/', ky_luat_cho_duyet, name='ky_luat_cho_duyet'),
    # path('ky-luat-nhan-vien/', ky_luat_nhan_vien, name='ky_luat_nhan_vien'),
path('ky-luat-khen-thuong/', ky_luat_khen_thuong, name='ky_luat_khen_thuong'),
]