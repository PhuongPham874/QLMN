from django import forms
from HOME.models import NhanVien,BHXH,DONGBHXH
class BHXHform(forms.ModelForm):
    ten_nv = forms.ModelChoiceField(
        queryset=NhanVien.objects.none(),  # sẽ set lại trong view
        required=True,
        label="Tên nhân viên",
        widget=forms.Select(attrs={'class': 'form-control'}))
    ma_BHXH= forms.CharField(
        required=False,
        label="Mã BHXH",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nhan_vien_dong = forms.DecimalField(
        required=False,
        label="Mức đóng của nhân viên(%)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    truong_dong = forms.DecimalField(
        required=False,
        label="Mức đóng của trường(%)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    thoi_gian_bat_dau = forms.DateField(
        required=False,
        label="Ngày bắt đầu đóng",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    class Meta:
        model = BHXH
        fields = ['ten_nv','ma_BHXH', 'nhan_vien_dong', 'truong_dong', 'thoi_gian_bat_dau']
class updateBHXH(forms.ModelForm):
    ma_BHXH = forms.CharField(
        required=False,
        label="Mã BHXH",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = BHXH
        fields = ['ma_BHXH']
class DongBHXHForm(forms.Form):
    ngay_bat_dau = forms.DateField(
        required=True,
        label="Ngày bắt đầu",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    ngay_ket_thuc = forms.DateField(
        required=True,
        label="Ngày kết thúc",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )


