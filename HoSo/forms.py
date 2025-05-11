from django import forms
from HOME.models import NhanVien, HopDongLaoDong


class NhanVienForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        fields = ['ten_nv', 'anh_ca_nhan', 'gioi_tinh', 'ngay_sinh', 'so_dien_thoai', 'email',
                  'so_cccd', 'vi_tri_cong_viec', 'to_phong_ban', 'trinh_do_hoc_van', 'chuyen_nganh',
                  'noi_dao_tao', 'nam_tn', 'ngay_cap', 'noi_cap', 'dia_chi_tam_tru']


class HopDongLaoDongForm(forms.ModelForm):
    class Meta:
        model = HopDongLaoDong
        exclude = ['nhan_vien', 'vi_tri_lam_viec', 'to_phong_ban']
        # hoặc dùng fields nếu bạn muốn liệt kê rõ ràng

    def __init__(self, *args, **kwargs):
        self.nhan_vien_instance = kwargs.pop('nhan_vien', None)
        super().__init__(*args, **kwargs)
