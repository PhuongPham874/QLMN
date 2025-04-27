from django.urls import path
from .views import danh_sach_nhan_vien,   hosochitiet, them_moi_ho_so, nv_hosochitiet, them_moi_hop_dong,hosochitietHDLD, nv_hosochitietHDLD  # Chú ý tên hàm

urlpatterns = [
    path('dsnhanvien/', danh_sach_nhan_vien, name='DanhSachNhanVien'),
    path('hosochitiet/<int:id>/', hosochitiet, name='QLXemHoSo'),
    path('hosochitietHDLD/<int:id>/', hosochitietHDLD, name='QLXemHoSoHDLD'),
    path('themmoihoso/', them_moi_ho_so, name='ThemMoiHoSo'),
    path('themmoi_hdld/', them_moi_hop_dong, name='themmoi_hdld'),  # Đảm bảo tên đúng
    path('nvhosochitiet/', nv_hosochitiet, name="NVXemHoSo"),
    path('nvhosochitietHDLD/', nv_hosochitietHDLD, name="NVXemHoSoHDLD"),
]



