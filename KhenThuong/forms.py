from django import forms
from HOME.models import KhenThuong, NhanVien

class KhenThuongForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Giới hạn nguoi_tao_don: không phải Giáo viên
        self.fields['nguoi_tao_don'].queryset = NhanVien.objects.exclude(vi_tri_cong_viec='Giáo viên')
        # Giới hạn nguoi_xac_nhan: chỉ Hiệu trưởng, Hiệu phó chuyên môn, Hiệu phó hoạt động
        self.fields['nguoi_xac_nhan'].queryset = NhanVien.objects.filter(
            vi_tri_cong_viec__in=['Hiệu trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']
        )
        # Ẩn trường trang_thai
        self.fields['trang_thai'].widget = forms.HiddenInput()

    class Meta:
        model = KhenThuong
        fields = ['nhan_vien', 'gia_tri', 'ly_do', 'nguoi_tao_don', 'nguoi_xac_nhan', 'trang_thai', 'minh_chung_file', 'minh_chung_url']
        widgets = {
            'nhan_vien': forms.Select(attrs={'class': 'form-control'}),
            'gia_tri': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ly_do': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nguoi_tao_don': forms.Select(attrs={'class': 'form-control'}),
            'nguoi_xac_nhan': forms.Select(attrs={'class': 'form-control'}),
            'minh_chung_file': forms.FileInput(attrs={'class': 'form-control'}),
            'minh_chung_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nhan_vien': 'Nhân viên',
            'gia_tri': 'Giá trị',
            'ly_do': 'Lý do',
            'nguoi_tao_don': 'Người tạo đơn',
            'nguoi_xac_nhan': 'Người duyệt đơn',  # Đổi tên hiển thị
            'minh_chung_file': 'Minh chứng (File)',
            'minh_chung_url': 'Minh chứng (URL)',
        }
        help_texts = {
            'nhan_vien': 'Chọn nhân viên nhận khen thưởng.',
            'gia_tri': 'Nhập giá trị khen thưởng (ví dụ: 100000.00).',
            'ly_do': 'Nhập lý do khen thưởng.',
            'nguoi_tao_don': 'Chọn nhân viên tạo đơn (không phải Giáo viên).',
            'nguoi_xac_nhan': 'Chọn nhân viên duyệt đơn (Hiệu trưởng/Hiệu phó).',  # Đổi tên hiển thị
            'minh_chung_file': 'Tải lên file minh chứng (PDF, hình ảnh, v.v.).',
            'minh_chung_url': 'Nhập URL minh chứng nếu có.',
        }