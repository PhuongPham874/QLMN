
from .views import (danh_sach_nhan_vien, hosochitiet, Add_ho_so, edit_ho_so, nv_hosochitiet,
                    them_moi_hop_dong, hosochitietHDLD, nv_hosochitietHDLD, edit_hdld,
                    redirect_hoso_view)  # Chú ý tên hàm
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
urlpatterns = [
    path('home/HoSo', redirect_hoso_view , name='Redirect_hoso_view'),
    path('dsnhanvien/', danh_sach_nhan_vien, name='DanhSachNhanVien'),
    path('hosochitiet/<int:id>/', hosochitiet, name='QLXemHoSo'),
    path('hosochitiet/<int:id>/edit/', edit_ho_so, name='edit_ho_so'),
    path('hosochitietHDLD/<int:nhan_vien_id>/', hosochitietHDLD, name='QLXemHoSoHDLD'),
    path('hosochitietHDLD/<int:nhan_vien_id>/edit/', edit_hdld, name='edit_hdld'),
    path('home/themmoihoso/', Add_ho_so, name='ThemMoiHoSo'),
    path('themmoi_hdld/<int:nhan_vien_id>/', them_moi_hop_dong, name='themmoi_hdld'),  # Đảm bảo tên đúng
    path('nvhosochitiet/', nv_hosochitiet, name="NVXemHoSo"),
    path('nvhosochitietHDLD/', nv_hosochitietHDLD, name="NVXemHoSoHDLD"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


