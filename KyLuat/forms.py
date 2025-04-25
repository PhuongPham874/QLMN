from django import forms
from HOME.models import KyLuat, NhanVien

class KyLuatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Giới hạn nguoi_tao_don: Chỉ Hiệu trưởng, Hiệu phó, hoặc Tổ trưởng
        self.fields['nguoi_tao_don'].queryset = NhanVien.objects.filter(
            chuc_vu__in=['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng']
        )

        # Giới hạn nguoi_duyet_don: Chỉ Hiệu trưởng, Hiệu phó
        self.fields['nguoi_duyet_don'].queryset = NhanVien.objects.filter(
            chuc_vu__in=['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']
        )

        # Lọc danh sách nhân viên theo to_phong_ban nếu người dùng là Tổ trưởng
        if self.request and hasattr(self.request, 'user'):
            try:
                nhan_vien = NhanVien.objects.get(user=self.request.user)
                if nhan_vien.chuc_vu == 'Tổ trưởng':
                    # Chỉ hiển thị nhân viên trong cùng to_phong_ban
                    self.fields['nhan_vien'].queryset = NhanVien.objects.filter(
                        to_phong_ban=nhan_vien.to_phong_ban
                    )
                elif nhan_vien.chuc_vu in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']:
                    # Hiệu trưởng/Hiệu phó thấy tất cả nhân viên
                    self.fields['nhan_vien'].queryset = NhanVien.objects.all()
                else:
                    # Giáo viên hoặc nhân viên khác không được tạo đơn
                    self.add_error(None, "Bạn không có quyền tạo đơn kỷ luật.")
            except NhanVien.DoesNotExist:
                self.add_error(None, "Không tìm thấy thông tin nhân viên của bạn.")

        # Ẩn và gán giá trị mặc định cho trang_thai
        self.fields['trang_thai'].widget = forms.HiddenInput()
        self.fields['trang_thai'].initial = 'DANG_CHO_DUYET'

        # Gán nguoi_tao_don mặc định
        if self.request and hasattr(self.request, 'user'):
            try:
                nhan_vien = NhanVien.objects.get(user=self.request.user)
                if nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng']:
                    self.add_error(None, "Bạn không có quyền tạo đơn kỷ luật.")
                else:
                    self.fields['nguoi_tao_don'].initial = nhan_vien
            except NhanVien.DoesNotExist:
                self.add_error(None, "Không tìm thấy thông tin nhân viên của bạn.")

    class Meta:
        model = KyLuat
        fields = ['nhan_vien', 'ngay_bat_dau', 'ngay_ra_quyet_dinh', 'ngay_ket_thuc', 'muc_do', 'so_tien_phat', 'ly_do',
                  'nguoi_tao_don', 'nguoi_duyet_don', 'trang_thai', 'minh_chung_file', 'minh_chung_url']
        widgets = {
            'nhan_vien': forms.Select(attrs={'class': 'form-control'}),
            'ngay_bat_dau': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_ra_quyet_dinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_ket_thuc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'muc_do': forms.Select(attrs={'class': 'form-control'}),
            'so_tien_phat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ly_do': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nguoi_tao_don': forms.Select(attrs={'class': 'form-control'}),
            'nguoi_duyet_don': forms.Select(attrs={'class': 'form-control'}),
            'trang_thai': forms.HiddenInput(attrs={'value': 'DANG_CHO_DUYET'}),
            'minh_chung_file': forms.FileInput(attrs={'class': 'form-control'}),
            'minh_chung_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nhan_vien': 'Nhân viên',
            'ngay_bat_dau': 'Ngày bắt đầu',
            'ngay_ra_quyet_dinh': 'Ngày ra quyết định',
            'ngay_ket_thuc': 'Ngày kết thúc',
            'muc_do': 'Mức độ',
            'so_tien_phat': 'Số tiền phạt',
            'ly_do': 'Lý do',
            'nguoi_tao_don': 'Người tạo đơn',
            'nguoi_duyet_don': 'Người duyệt đơn',
            'minh_chung_file': 'Minh chứng (File)',
            'minh_chung_url': 'Minh chứng (URL)',
        }
        help_texts = {
            'nhan_vien': 'Chọn nhân viên bị kỷ luật.',
            'ngay_bat_dau': 'Ngày bắt đầu kỷ luật.',
            'ngay_ra_quyet_dinh': 'Ngày ra quyết định kỷ luật.',
            'ngay_ket_thuc': 'Ngày kết thúc kỷ luật (bắt buộc cho Kỷ luật 3 tháng hoặc 6 tháng).',
            'muc_do': 'Chọn mức độ kỷ luật.',
            'so_tien_phat': 'Nhập số tiền phạt nếu chọn Phạt tiền.',
            'ly_do': 'Nhập lý do kỷ luật.',
            'nguoi_tao_don': 'Chọn nhân viên tạo đơn.',
            'nguoi_duyet_don': 'Chọn nhân viên duyệt đơn.',
            'minh_chung_file': 'Tải lên file minh chứng (PDF, hình ảnh, v.v.).',
            'minh_chung_url': 'Nhập URL minh chứng nếu có.',
        }

    def clean(self):
        cleaned_data = super().clean()
        muc_do = cleaned_data.get('muc_do')
        so_tien_phat = cleaned_data.get('so_tien_phat')
        minh_chung_file = cleaned_data.get('minh_chung_file')
        minh_chung_url = cleaned_data.get('minh_chung_url')
        ngay_ra_quyet_dinh = cleaned_data.get('ngay_ra_quyet_dinh')
        nguoi_tao_don = cleaned_data.get('nguoi_tao_don')
        nguoi_duyet_don = cleaned_data.get('nguoi_duyet_don')
        ly_do = cleaned_data.get('ly_do')
        ngay_ket_thuc = cleaned_data.get('ngay_ket_thuc')
        ngay_bat_dau = cleaned_data.get('ngay_bat_dau')

        cleaned_data['trang_thai'] = cleaned_data.get('trang_thai') or 'DANG_CHO_DUYET'

        if not ngay_ra_quyet_dinh:
            self.add_error('ngay_ra_quyet_dinh', "Ngày ra quyết định là bắt buộc.")
        if not nguoi_tao_don:
            self.add_error('nguoi_tao_don', "Người tạo đơn là bắt buộc.")
        if not nguoi_duyet_don and self.fields['nguoi_duyet_don'].queryset.exists():
            self.add_error('nguoi_duyet_don', "Người duyệt đơn là bắt buộc.")
        if not ly_do:
            self.add_error('ly_do', "Lý do kỷ luật là bắt buộc.")
        if muc_do == 'PHAT_TIEN':
            if not so_tien_phat or so_tien_phat <= 0:
                self.add_error('so_tien_phat', "Số tiền phạt phải lớn hơn 0 khi mức độ là Phạt tiền.")
        if muc_do in ['KY_LUAT_3_THANG', 'KY_LUAT_6_THANG'] and not (minh_chung_file or minh_chung_url):
            self.add_error(None, "Minh chứng (file hoặc URL) là bắt buộc cho Kỷ luật 3 tháng hoặc 6 tháng.")
        if minh_chung_file and minh_chung_url:
            self.add_error(None, "Chỉ được cung cấp một loại minh chứng: file hoặc URL.")
        if muc_do in ['KY_LUAT_3_THANG', 'KY_LUAT_6_THANG'] and not ngay_ket_thuc:
            self.add_error('ngay_ket_thuc', "Ngày kết thúc là bắt buộc cho Kỷ luật 3 tháng hoặc 6 tháng.")
        if ngay_ket_thuc and ngay_bat_dau and ngay_ket_thuc <= ngay_bat_dau:
            self.add_error('ngay_ket_thuc', "Ngày kết thúc phải sau ngày bắt đầu.")

        return cleaned_data