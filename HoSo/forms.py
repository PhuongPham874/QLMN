from django import forms
from HOME.models import NhanVien, HopDongLaoDong


class NhanVienForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        exclude = ['user']

    def clean_so_cccd(self):
        so_cccd = self.cleaned_data.get('so_cccd')
        if not so_cccd.isdigit() or len(so_cccd) != 12:
            raise forms.ValidationError("Số CCCD phải đúng 12 chữ số.")
        return so_cccd

    def clean_so_dien_thoai(self):
        so_dt = self.cleaned_data.get('so_dien_thoai')
        if not so_dt.isdigit() or len(so_dt) != 10:
            raise forms.ValidationError("Số điện thoại phải đúng 10 chữ số.")
        return so_dt

class HopDongLaoDongForm(forms.ModelForm):
    class Meta:
        model = HopDongLaoDong
        exclude = ['nhan_vien']

    def __init__(self, *args, **kwargs):
        self.nhan_vien_instance = kwargs.pop('nhan_vien', None)
        super().__init__(*args, **kwargs)
