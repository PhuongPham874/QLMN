

from django import forms
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from HOME.models import NghiPhep, NhanVien

loai_nghi_phep = (
    ("Nghỉ ốm", "Nghỉ ốm"),
    ("Nghỉ phép năm", "Nghỉ phép năm") )


class NghiPhepForm(forms.ModelForm):
    loai_nghi = forms.ChoiceField(required=False, choices=loai_nghi_phep, label="Chọn loại nghỉ phép:",
                                  widget=forms.Select(attrs={'class': 'label'})
                                  )
    ngay_bat_dau = forms.DateField(
        label="Ngày bắt đầu",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'label'})
    )
    ngay_ket_thuc = forms.DateField(
        label="Ngày kết thúc",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'label'})
    )

    ly_do = forms.CharField(
        label="Lý do",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    class Meta:
        model = NghiPhep
        exclude = ["ghi_chu", "nhan_vien", "trang_thai_don","ngay_tao_don","ngay_chinh_sua","nguoi_duyet","ngay_duyet"]

    def clean(self):
        cleaned_data = super().clean()
        so_cccd = cleaned_data.get('so_cccd')
        so_dien_thoai = cleaned_data.get('so_dien_thoai')

        # Kiểm tra CCCD: đúng 12 chữ số
        if so_cccd and (not so_cccd.isdigit() or len(so_cccd) != 12):
            self.add_error('so_cccd', "Số CCCD phải đúng 12 chữ số.")

        # Kiểm tra SĐT: đúng 10 chữ số
        if so_dien_thoai and (not so_dien_thoai.isdigit() or len(so_dien_thoai) != 10):
            self.add_error('so_dien_thoai', "Số điện thoại phải đúng 10 chữ số.")


class SearchForm(forms.Form):
    search = forms.DateField(
        required=True,
        label="Tìm kiếm ngày bắt đầu nghỉ:",
        widget=forms.DateInput(attrs={'type': 'date','placeholder': 'Ngày bắt đầu nghỉ'})
    )

class SearchNVForm(forms.Form):
    nhan_vien = forms.ModelChoiceField(
        queryset=NhanVien.objects.all(),
        label='Chọn nhân viên',
        required=False,
        empty_label="-- Chọn nhân viên --",
        widget=forms.Select(attrs={
            'style': (
                'border: none; '
                'border-radius: 8px; '
                'padding: 8px 12px; '
                'font-size: 16px; '
                'box-shadow: inset 0 0 3px rgba(0,0,0,0.1); '
                'outline: none;'
            )
        })

    )

class Ghichu(forms.Form):
    ghi_chu = forms.CharField( required=False,label="",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )


