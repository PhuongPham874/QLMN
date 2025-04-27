from django.core.validators import MinValueValidator
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from .models import NhanVien, HopDongLaoDong

class NhanVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    ten_nv = models.CharField(max_length=100)
    chuc_vu = models.CharField(max_length=50, null=True)
    anh_ca_nhan = models.ImageField(upload_to='media/nhanvien/')
    gioi_tinh = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
    ngay_sinh = models.DateField()
    so_dien_thoai = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', message="Số điện thoại phải có đúng 10 chữ số.")]
    )
    email = models.EmailField(unique=True)
    so_cccd = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(r'^\d{12}$', message="Số CCCD phải có đúng 12 chữ số.")]
    )
    vi_tri_cong_viec = models.CharField(max_length=30)
    TO_PHONG_BAN_CHOICES = [
        ('Lớp mầm', 'Lớp mầm'),
        ('Lớp chồi', 'Lớp chồi'),
        ('Lớp lá', 'Lớp lá'),
        ('Văn phòng', 'Văn phòng'),
        ('Y tế - Hậu cần', 'Y tế - Hậu cần'),
        ('Ban giám hiệu', 'Ban giám hiệu'),
    ]
    to_phong_ban = models.CharField(max_length=50, choices=TO_PHONG_BAN_CHOICES)
    TRINH_DO_HOC_VAN_CHOICES = [
        ('Dưới trung cấp', 'Dưới trung cấp'),
        ('Trung cấp', 'Trung cấp'),
        ('Cao đẳng', 'Cao đẳng'),
        ('Đại học', 'Đại học'),
        ('Thạc sĩ', 'Thạc sĩ'),
    ]
    trinh_do_hoc_van = models.CharField(max_length=50, choices=TRINH_DO_HOC_VAN_CHOICES)
    chuyen_nganh = models.CharField(max_length=100)
    noi_dao_tao = models.CharField(max_length=100)
    nam_tn = models.IntegerField()
    ngay_cap = models.DateField()
    noi_cap = models.CharField(max_length=100)
    dia_chi_tam_tru = models.TextField()

    def __str__(self):
        return self.ten_nv

class HopDongLaoDong(models.Model):
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)  # Liên kết với nhân viên


        # Tạo mã nhân viên tự động sinh
    ma_nhan_vien = models.CharField(max_length=20, unique=True, blank=True, null=True)

        # Các trường thông tin hợp đồng lao động
    vi_tri_lam_viec = models.CharField(max_length=50)  # Vị trí làm việc của nhân viên
    to_phong_ban = models.CharField(max_length=50)  # Tổ phòng ban của nhân viên
    loai_hop_dong = models.CharField(max_length=100, choices=[  # Loại hợp đồng
        ('Hợp đồng thử việc', 'Hợp đồng thử việc'),
        ('Hợp đồng có thời hạn', 'Hợp đồng có thời hạn')
    ])
    luong = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])  # Mức lương
    ngay_ky = models.DateField()  # Ngày ký hợp đồng
    tu_ngay = models.DateField()  # Ngày bắt đầu hợp đồng
    den_ngay = models.DateField()  # Ngày kết thúc hợp đồng

        # Trạng thái hợp đồng (Đang hiệu lực, Sắp hết hạn, Đã chấm dứt)
    TRANG_THAI_HOP_DONG_CHOICES = [
        ('Đang hiệu lực', 'Đang hiệu lực'),
        ('Sắp hết hạn', 'Sắp hết hạn'),
        ('Đã chấm dứt', 'Đã chấm dứt')
    ]
    trang_thai_hop_dong = models.CharField(max_length=50,
                                            choices=TRANG_THAI_HOP_DONG_CHOICES)  # Trạng thái hợp đồng

        # Các trường 'choices' giống như phần model nhân viên
    TO_PHONG_BAN_CHOICES = [
            ('Lớp mầm', 'Lớp mầm'),
            ('Lớp chồi', 'Lớp chồi'),
            ('Lớp lá', 'Lớp lá'),
            ('Văn phòng', 'Văn phòng'),
            ('Y tế - Hậu cần', 'Y tế - Hậu cần'),
        ]
    VI_TRI_LAM_VIEC_CHOICES = [
            ('Giáo viên', 'Giáo viên'),
            ('Nhân viên văn phòng', 'Nhân viên văn phòng'),
            ('Quản lý', 'Quản lý'),
        ]

        # Các trường choices
    to_phong_ban = models.CharField(max_length=50, choices=TO_PHONG_BAN_CHOICES)  # Tổ phòng ban với choices
    vi_tri_lam_viec = models.CharField(max_length=50,
                                           choices=VI_TRI_LAM_VIEC_CHOICES)  # Vị trí làm việc với choices

        # Danh sách phụ cấp
    class PhuCap(models.Model):
        hop_dong = models.ForeignKey(HopDongLaoDong, related_name='phu_caps', on_delete=models.CASCADE)
        stt = models.IntegerField()  # Số thứ tự
        ten_phu_cap = models.CharField(max_length=100)  # Tên phụ cấp
        gia_tri = models.DecimalField(max_digits=15, decimal_places=2,
                                        validators=[MinValueValidator(0)])  # Giá trị phụ cấp

        def __str__(self):
            return f"{self.stt} - {self.ten_phu_cap}"

        def save(self, *args, **kwargs):
            # Gán thông tin nhân viên vào các trường hợp đồng lao động khi lưu
            if not self.vi_tri_lam_viec:
                self.vi_tri_lam_viec = self.nhan_vien.vi_tri_cong_viec  # Lấy vị trí làm việc từ nhân viên
            if not self.to_phong_ban:
                self.to_phong_ban = self.nhan_vien.to_phong_ban  # Lấy tổ phòng ban từ nhân viên

            # Tạo mã nhân viên tự động nếu chưa có
            if not self.ma_nhan_vien:
                last_nhan_vien = HopDongLaoDong.objects.all().order_by(
                    'id').last()  # Lấy đối tượng hợp đồng lao động cuối
                last_id = last_nhan_vien.id if last_nhan_vien else 0  # Nếu không có thì gán giá trị 0
                self.ma_nhan_vien = f"NV{last_id + 1:03d}"  # Tạo mã nhân viên theo định dạng NV001, NV002, ...

            super(HopDongLaoDong, self).save(*args, **kwargs)

        def __str__(self):
            return f"{self.nhan_vien.ten_nv} - {self.loai_hop_dong}"

    def __str__(self):
        return f"{self.nhan_vien.ten_nv} - {self.loai_hop_dong}"