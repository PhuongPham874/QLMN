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
        fields = ['nhan_vien', 'vi_tri_lam_viec', 'to_phong_ban', 'so_hop_dong', 'thoi_han_hop_dong', 'loai_hop_dong', 'luong', 'ngay_ky', 'tu_ngay', 'den_ngay', 'trang_thai_hop_dong']

    def __init__(self, *args, **kwargs):
        nhan_vien = kwargs.pop('nhan_vien', None)
        super().__init__(*args, **kwargs)

        if nhan_vien:
            self.fields['nhan_vien'].initial = nhan_vien
            self.fields['vi_tri_lam_viec'].initial = nhan_vien.vi_tri_cong_viec
            self.fields['to_phong_ban'].initial = nhan_vien.to_phong_ban
