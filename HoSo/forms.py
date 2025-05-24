from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from HOME.models import NhanVien, HopDongLaoDong


class NhanVienForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        exclude = ['user']

    def clean(self):
        cleaned_data = super().clean()

        # Danh sách trường bắt buộc
        required_fields = [
            'ten_nv', 'gioi_tinh','anh_ca_nhan' , 'ngay_sinh', 'vi_tri_cong_viec', 'to_phong_ban',
            'trinh_do_hoc_van', 'chuyen_nganh', 'noi_dao_tao', 'nam_tn', 'ngay_cap',
            'noi_cap', 'dia_chi_tam_tru', 'chuc_vu', 'so_dien_thoai', 'email', 'so_cccd'
        ]

        missing_fields = [field for field in required_fields if not cleaned_data.get(field)]
        if missing_fields:
            raise ValidationError("Vui lòng nhập đủ các thông tin bắt buộc.")

    def clean_so_cccd(self):
        so_cccd = self.cleaned_data.get('so_cccd')
        if not so_cccd:
            raise forms.ValidationError("Vui lòng nhập số CCCD")
        if not so_cccd.isdigit() or len(so_cccd) != 12:
            raise forms.ValidationError("Số CCCD phải đúng 12 chữ số.")
        return so_cccd

    def clean_so_dien_thoai(self):
        so_dt = self.cleaned_data.get('so_dien_thoai')
        if not so_dt:
            raise forms.ValidationError("Vui lòng nhập số điện thoại")
        if not so_dt.isdigit() or len(so_dt) != 10:
            raise forms.ValidationError("Số điện thoại phải đúng 10 chữ số.")
        return so_dt
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Vui lòng nhập đủ thông tin")
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Email không hợp lệ")
        return email

class HopDongLaoDongForm(forms.ModelForm):
    class Meta:
        model = HopDongLaoDong
        exclude = ['to_phong_ban', 'vi_tri_lam_viec', 'nhan_vien']

    def __init__(self, *args, **kwargs):
        self.nhan_vien_instance = kwargs.pop('nhan_vien', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        required_fields = [
            'so_hop_dong', 'thoi_han_hop_dong',
            'loai_hop_dong', 'luong', 'ngay_ky', 'tu_ngay', 'den_ngay', 'trang_thai_hop_dong'
        ]

        missing_fields = [field for field in required_fields if not cleaned_data.get(field)]
        if missing_fields:
            raise ValidationError("Vui lòng nhập đủ các thông tin bắt buộc.")

        # Kiểm tra ngày bắt đầu <= ngày kết thúc
        tu_ngay = cleaned_data.get('tu_ngay')
        den_ngay = cleaned_data.get('den_ngay')
        if tu_ngay and den_ngay and tu_ngay > den_ngay:
            raise ValidationError("Ngày 'từ ngày' phải nhỏ hơn hoặc bằng 'đến ngày'.")

        # Kiểm tra lương không âm
        luong = cleaned_data.get('luong')
        if luong is not None and luong < 0:
            raise ValidationError("Lương phải là số không âm.")

        return cleaned_data
