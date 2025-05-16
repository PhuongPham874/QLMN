

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
        start = cleaned_data.get('ngay_bat_dau')
        end = cleaned_data.get('ngay_ket_thuc')
        now = timezone.now().date()

        if start and end and end < start:
            self.add_error('ngay_ket_thuc', "Ngày kết thúc không được nhỏ hơn ngày bắt đầu.")
        if start < now:
            self.add_error('ngay_bat_dau', "Ngày bắt đầu không được nhỏ hơn ngày hiện tại.")


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