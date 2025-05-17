from django import forms
from HOME.models import KhenThuong, NhanVien

class KhenThuongForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Lấy user từ kwargs
        self.user = user  # Lưu user vào self.user để sử dụng trong clean
        super().__init__(*args, **kwargs)

        # Xác định người dùng hiện tại
        nhan_vien = None
        if user:
            try:
                nhan_vien = NhanVien.objects.get(user=user)
            except NhanVien.DoesNotExist:
                self.add_error(None, "Không tìm thấy thông tin nhân viên của bạn.")

        # Tùy chỉnh label cho dropdown
        def get_label(obj):
            return f"{obj.ten_nv} ({obj.chuc_vu if obj.chuc_vu else 'N/A'})"

        # Giới hạn nguoi_tao_don: chỉ Tổ trưởng, Hiệu trưởng, Hiệu phó chuyên môn, Hiệu phó hoạt động
        self.fields['nguoi_tao_don'].queryset = NhanVien.objects.filter(
            chuc_vu__in=['Tổ trưởng', 'Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']
        )
        self.fields['nguoi_tao_don'].widget.attrs['readonly'] = True
        self.fields['nguoi_tao_don'].widget.attrs['class'] = 'form-control'
        self.fields['nguoi_tao_don'].label_from_instance = get_label

        # Nếu người tạo là Hiệu Trưởng, tự động duyệt đơn
        if nhan_vien and nhan_vien.chuc_vu == 'Hiệu Trưởng':
            self.fields['nguoi_xac_nhan'].required = False
            self.fields['nguoi_xac_nhan'].widget = forms.HiddenInput()
            self.fields['nguoi_xac_nhan'].initial = nhan_vien
            self.fields['trang_thai'].initial = 'DA_DUYET'
        else:
            # Giới hạn nguoi_xac_nhan: chỉ Hiệu trưởng, Hiệu phó chuyên môn, Hiệu phó hoạt động
            self.fields['nguoi_xac_nhan'].queryset = NhanVien.objects.filter(
                chuc_vu__in=['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']
            )
            self.fields['nguoi_xac_nhan'].required = True
            self.fields['nguoi_xac_nhan'].label_from_instance = get_label
            self.fields['trang_thai'].initial = 'DANG_CHO_DUYET'

        # Giới hạn nhan_vien dựa trên chức vụ và vị trí công việc
        if nhan_vien:
            if nhan_vien.chuc_vu == 'Tổ trưởng':
                self.fields['nhan_vien'].queryset = NhanVien.objects.filter(
                    to_phong_ban=nhan_vien.to_phong_ban
                )
            elif nhan_vien.chuc_vu == 'Hiệu phó chuyên môn':
                self.fields['nhan_vien'].queryset = NhanVien.objects.filter(
                    vi_tri_cong_viec__in=['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh']
                )
            elif nhan_vien.chuc_vu == 'Hiệu phó hoạt động':
                self.fields['nhan_vien'].queryset = NhanVien.objects.filter(
                    vi_tri_cong_viec__in=['Bếp', 'Y - tế']
                )
            elif nhan_vien.chuc_vu == 'Hiệu Trưởng':
                self.fields['nhan_vien'].queryset = NhanVien.objects.all()
            else:
                self.add_error(None, "Bạn không có quyền tạo đơn khen thưởng.")

        # Ẩn trường trang_thai
        self.fields['trang_thai'].widget = forms.HiddenInput()

        # Gán nguoi_tao_don mặc định
        if nhan_vien:
            self.fields['nguoi_tao_don'].initial = nhan_vien

    class Meta:
        model = KhenThuong
        fields = ['nhan_vien', 'gia_tri', 'ly_do', 'nguoi_tao_don', 'nguoi_xac_nhan', 'trang_thai', 'minh_chung_file', 'minh_chung_url']
        widgets = {
            'nhan_vien': forms.Select(attrs={'class': 'form-control'}),
            'gia_tri': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ly_do': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nguoi_xac_nhan': forms.Select(attrs={'class': 'form-control'}),
            'minh_chung_file': forms.FileInput(attrs={'class': 'form-control'}),
            'minh_chung_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nhan_vien': 'Nhân viên',
            'gia_tri': 'Giá trị',
            'ly_do': 'Lý do',
            'nguoi_tao_don': 'Người tạo đơn',
            'nguoi_xac_nhan': 'Người duyệt đơn',
            'minh_chung_file': 'Minh chứng (File)',
            'minh_chung_url': 'Minh chứng (URL)',
        }
        help_texts = {
            'nhan_vien': 'Chọn nhân viên nhận khen thưởng.',
            'gia_tri': 'Nhập giá trị khen thưởng (ví dụ: 100000.00).',
            'ly_do': 'Nhập lý do khen thưởng.',
            'nguoi_tao_don': 'Nhân viên tạo đơn (không thể chỉnh sửa).',
            'nguoi_xac_nhan': 'Chọn nhân viên duyệt đơn (Hiệu Trưởng/Hiệu phó).',
            'minh_chung_file': 'Tải lên file minh chứng (PDF, hình ảnh, v.v.).',
            'minh_chung_url': 'Nhập URL minh chứng nếu có.',
        }

    def clean(self):
        cleaned_data = super().clean()
        gia_tri = cleaned_data.get('gia_tri')
        minh_chung_file = cleaned_data.get('minh_chung_file')
        minh_chung_url = cleaned_data.get('minh_chung_url')
        nguoi_tao_don = cleaned_data.get('nguoi_tao_don')
        nguoi_xac_nhan = cleaned_data.get('nguoi_xac_nhan')
        ly_do = cleaned_data.get('ly_do')

        # Kiểm tra nếu người tạo là Hiệu Trưởng
        nhan_vien = None
        if self.user:
            try:
                nhan_vien = NhanVien.objects.get(user=self.user)
            except NhanVien.DoesNotExist:
                pass

        if nhan_vien and nhan_vien.chuc_vu == 'Hiệu Trưởng':
            cleaned_data['trang_thai'] = 'DA_DUYET'
            cleaned_data['nguoi_xac_nhan'] = nhan_vien
        else:
            if not nguoi_xac_nhan and self.fields['nguoi_xac_nhan'].queryset.exists():
                self.add_error('nguoi_xac_nhan', "Người duyệt đơn là bắt buộc.")

        if not nguoi_tao_don:
            self.add_error('nguoi_tao_don', "Người tạo đơn là bắt buộc.")
        if not ly_do:
            self.add_error('ly_do', "Lý do khen thưởng là bắt buộc.")
        if not gia_tri or gia_tri <= 0:
            self.add_error('gia_tri', "Giá trị khen thưởng phải lớn hơn 0.")
        if minh_chung_file and minh_chung_url:
            self.add_error(None, "Chỉ được cung cấp một loại minh chứng: file hoặc URL.")

        return cleaned_data