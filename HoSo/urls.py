from django.urls import path
from .views import danh_sach_nhan_vien,hoso,them_moi_ho_so,nv_hosochitiet

urlpatterns = [
    path('dsnhanvien/', danh_sach_nhan_vien, name='DanhSachNhanVien'),
    path('hosochitiet/<int:id>/', hoso, name='HoSoChiTiet'),#admin
    path('themmoihoso/', them_moi_ho_so, name='ThemMoiHoSo'),
    path('nvhosochitiet/', nv_hosochitiet, name="NVXemHoSo"),#nhanvien
]