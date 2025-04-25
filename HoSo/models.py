from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class NhanVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    ten_nv = models.CharField(max_length=50)
    anh_ca_nhan = models.CharField(max_length=255, null=True, blank=True)
    so_cccd = models.CharField(
        max_length=12, unique=True,
        validators=[RegexValidator(r'^\d{12}$', message="Số CCCD phải có đúng 12 chữ số.")]
    )
    ngay_sinh = models.DateField()
    dia_chi = models.TextField()
    so_dien_thoai = models.CharField(
        max_length=10, unique=True,
        validators=[RegexValidator(r'^\d{10}$', message="Số điện thoại phải có đúng 10 chữ số.")]
    )
    email = models.EmailField(unique=True)
    trinh_do_hoc_van = models.CharField(max_length=50)
    kinh_nghiem_lam_viec = models.PositiveIntegerField(default=0)
    vi_tri_cong_viec = models.CharField(max_length=50)

    def __str__(self):
        return self.ten_nv


class HopDongLaoDong(models.Model):
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    loai_hop_dong = models.CharField(max_length=100)
    thoi_han_hop_dong = models.CharField(max_length=20)
    ngay_vao_lam = models.DateField()
    muc_luong = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    trang_thai_hop_dong = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nhan_vien.ten_nv} - {self.loai_hop_dong} ({self.trang_thai_hop_dong})"

class BHXH(models.Model):
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    nhan_vien_dong = models.DecimalField(max_digits=5, decimal_places=2, default=10.5)
    truong_dong = models.DecimalField(max_digits=5, decimal_places=2, default=21.5)
    thoi_gian_bat_dau_dong = models.DateField()
    def __str__(self):
        return f"{self.nhan_vien.ten_nv}"

class NghiPhep(models.Model):
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    loai_nghi = models.CharField(max_length=255)
    ngay_bat_dau = models.DateField()
    ngay_ket_thuc = models.DateField()
    ly_do = models.TextField()
    ngay_tao_don = models.DateTimeField(auto_now_add=True)
    trang_thai_don = models.CharField(max_length=255)
    ghi_chu = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nhan_vien.ten_nv} - {self.loai_nghi}"

class KyLuat(models.Model):
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    ngay_bat_dau = models.DateField()
    muc_do = models.CharField(max_length=100)
    ly_do = models.TextField()

    def get_all_info(self):
        return (f"Tên NV: {self.nhan_vien.ten_nv}, Ngày bắt đầu: {self.ngay_bat_dau},"
                f" Mức độ: {self.muc_do}, Lý do: {self.ly_do}")


class KhenThuong(models.Model):
    ngay_khen_thuong = models.DateField()
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    gia_tri = models.DecimalField(max_digits=10, decimal_places=2)
    ly_do = models.TextField()

class ChamCong(models.Model):
    TRANG_THAI_CHOICES = [
        (0, "Đúng giờ"),
        (1, "Nghỉ"),
        (2, "Muộn"),
    ]

    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    gio_vao = models.TimeField(null=True, blank=True, verbose_name="Giờ Vào")
    gio_ra = models.TimeField(null=True, blank=True, verbose_name="Giờ Ra")
    ngay = models.DateField(verbose_name="Ngày")
    trang_thai = models.IntegerField(choices=TRANG_THAI_CHOICES, verbose_name="Trạng Thái")
    class Meta:
        unique_together = ("nhan_vien", "ngay")  # Đảm bảo mỗi nhân viên chỉ có một bản ghi mỗi ngày
        ordering = ["ngay"]
    def __str__(self):
        return f"Nhân viên {self.nhan_vien} - {self.ngay} - {self.get_trang_thai_display()}"





