from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class PhuCap(models.Model):
   ten_phu_cap = models.CharField(max_length=100)
   gia_tri = models.DecimalField(max_digits=10, decimal_places=2)

   def __str__(self):
       return self.ten_phu_cap

TRINH_DO_HOC_VAN_CHOICES = [
    ('Dưới trung cấp', 'Dưới trung cấp'),
    ('Trung cấp', 'Trung cấp'),
    ('Cao đẳng', 'Cao đẳng'),
    ('Đại học', 'Đại học'),
    ('Thạc sĩ', 'Thạc sĩ'), ]
TO_PHONG_BAN_CHOICES = [
     ('Lớp mầm', 'Lớp mầm'),
     ('Lớp chồi', 'Lớp chồi'),
     ('Lớp lá', 'Lớp lá'),
     ('Văn phòng', 'Văn phòng'),
     ('Y tế - Hậu cần', 'Y tế - Hậu cần'),
    ('BGH', 'BGH'),
 ]

class NhanVien(models.Model):
 user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, null=False, related_name='nhanvien_home')
 ten_nv = models.CharField(max_length=100)
 anh_ca_nhan = models.ImageField(upload_to='nhanvien/', null=True, blank=True)
 gioi_tinh = models.CharField(max_length=10, choices=[('2', 'Nam'), ('1', 'Nữ')],default='1')
 ngay_sinh = models.DateField(null=True)
 vi_tri_cong_viec = models.CharField(max_length=100, blank=True, null=True)
 to_phong_ban = models.CharField(max_length=50, choices=TO_PHONG_BAN_CHOICES)
 trinh_do_hoc_van = models.CharField(max_length=50, choices=TRINH_DO_HOC_VAN_CHOICES)
 chuyen_nganh = models.CharField(max_length=100, null=True)
 noi_dao_tao = models.CharField(max_length=100)
 nam_tn = models.IntegerField(null=True)
 ngay_cap = models.DateField(null=True)
 noi_cap = models.CharField(max_length=100)
 dia_chi_tam_tru = models.TextField(null=True)
 chuc_vu = models.CharField(max_length=150, null=True)
 so_dien_thoai = models.CharField(
     max_length=10,
     unique=True)
 email = models.EmailField(unique=True, max_length=50, null=True)
 so_cccd = models.CharField(
     max_length=12,
     unique=True
 )
 phu_caps = models.ManyToManyField(PhuCap, through='PhuCapNhanVien',blank=True)

 class Meta:
     db_table = 'HOME_nhanvien'

 def __str__(self):
     return self.ten_nv








class PhuCapNhanVien(models.Model):
   nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
   phu_cap = models.ForeignKey(PhuCap, on_delete=models.CASCADE)


   def __str__(self):
       return f"{self.nhan_vien.ten_nv} - {self.phu_cap.ten_phu_cap}"




class HopDongLaoDong(models.Model):
   nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
   so_hop_dong = models.CharField(max_length=50)
   vi_tri_lam_viec = models.CharField(max_length=50, blank=False)
   to_phong_ban = models.CharField(max_length=50, blank=False)
   thoi_han_hop_dong = models.IntegerField(verbose_name='Thời hạn hợp đồng')
   loai_hop_dong = models.CharField(max_length=100, choices=[
       ('Hợp đồng thử việc', 'Hợp đồng thử việc'),
       ('Hợp đồng có thời hạn', 'Hợp đồng có thời hạn')], default='Hợp đồng thử việc')
   luong = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
   ngay_ky = models.DateField()
   tu_ngay = models.DateField()
   den_ngay = models.DateField()
   TRANG_THAI_HOP_DONG_CHOICES = [
       ('Đang hiệu lực', 'Đang hiệu lực'),
       ('Sắp hết hạn', 'Sắp hết hạn'),
       ('Hết hiệu lực', 'Hết hiệu lực')
   ]
   trang_thai_hop_dong = models.CharField(max_length=50,
                                          choices=TRANG_THAI_HOP_DONG_CHOICES)


def __str__(self):
   return f"{self.nhan_vien.ten_nv} - {self.loai_hop_dong}"











class BHXH(models.Model):
   nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
   ma_BHXH  = models.CharField(null=True,max_length=10,unique=True,
   validators=[RegexValidator(regex=r'^\d{10}$', message='Mã BHXH phải có đúng 10 chữ số')])
   nhan_vien_dong = models.DecimalField(max_digits=5, decimal_places=2, default=10.5)
   truong_dong = models.DecimalField(max_digits=5, decimal_places=2, default=21.5)
   thoi_gian_bat_dau = models.DateField(null=True)
   def __str__(self):
       return f"{self.nhan_vien.ten_nv}"




class DONGBHXH(models.Model):
  nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
  ngay_bat_dau = models.DateField(null=True)
  ngay_ket_thuc =  models.DateField(null=True)
  tong_tien = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
  def __str__(self):
       return f"{self.nhan_vien.ten_nv}"








class NghiPhep(models.Model):
   nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='nguoi_tao_don')
   loai_nghi = models.CharField(max_length=100)
   ngay_bat_dau = models.DateField(null=True)
   ngay_ket_thuc = models.DateField(null=True)
   ly_do = models.TextField()
   trang_thai_don = models.CharField(max_length=50, default='Đang chờ duyệt')
   ghi_chu = models.TextField(blank=True, null=True)
   ngay_tao_don = models.DateTimeField(null=True)
   ngay_chinh_sua = models.DateTimeField(null=True)
   nguoi_duyet = models.ForeignKey(NhanVien, null = True, on_delete=models.CASCADE, related_name='nguoi_duyet_don')
   ngay_duyet = models.DateField(blank=True, null=True)


   def __str__(self):
       return f"{self.nhan_vien} - {self.loai_nghi} ({self.ngay_bat_dau} đến {self.ngay_ket_thuc})"


class KyLuat(models.Model):
  MUC_DO_CHOICES = (
      ('KY_LUAT_3_THANG', 'Kỷ luật 3 tháng'),
      ('KY_LUAT_6_THANG', 'Kỷ luật 6 tháng'),
      ('PHAT_TIEN', 'Phạt tiền'),
  )
  TRANG_THAI_CHOICES = (
      ('DANG_CHO_DUYET', 'Đang chờ duyệt'),
      ('DA_DUYET', 'Đã duyệt'),
      ('DA_TU_CHOI', 'Đã từ chối'),
  )
  nhan_vien = models.ForeignKey('NhanVien', on_delete=models.CASCADE, related_name='ky_luat_nhan_vien')
  ngay_bat_dau = models.DateField(null=True)
  ngay_ra_quyet_dinh = models.DateField(null=True)
  ngay_ket_thuc = models.DateField(null=True, blank=True)
  muc_do = models.CharField(max_length=20, choices=MUC_DO_CHOICES)
  so_tien_phat = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
  ly_do = models.TextField(null=True)
  nguoi_tao_don = models.ForeignKey('NhanVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='ky_luat_tao')
  nguoi_duyet_don = models.ForeignKey('NhanVien', on_delete=models.SET_NULL,  null=True, blank=True, related_name='ky_luat_duyet')
  trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='DANG_CHO_DUYET')
  minh_chung_file = models.FileField(upload_to='minh_chung_ky_luat/', null=True, blank=True)
  minh_chung_url = models.URLField(max_length=200, null=True, blank=True)




  def get_all_info(self):
      so_tien = f", Số tiền phạt: {self.so_tien_phat}" if self.muc_do == 'PHAT_TIEN' and self.so_tien_phat else ""
      ngay_ket_thuc = f", Ngày kết thúc: {self.ngay_ket_thuc}" if self.ngay_ket_thuc else ""
      minh_chung = f", Minh chứng: {self.minh_chung_file.url if self.minh_chung_file else self.minh_chung_url if self.minh_chung_url else 'Không có'}"
      nguoi_tao_info = f"{self.nguoi_tao_don.ten_nv} ({self.nguoi_tao_don.chuc_vu})" if self.nguoi_tao_don else 'N/A'
      nguoi_duyet_info = f"{self.nguoi_duyet_don.ten_nv} ({self.nguoi_duyet_don.chuc_vu})" if self.nguoi_duyet_don else 'N/A'
      return (f"Tên NV: {self.nhan_vien.ten_nv}, Ngày ra quyết định: {self.ngay_ra_quyet_dinh}, "
              f"Ngày bắt đầu: {self.ngay_bat_dau}{ngay_ket_thuc}, "
              f"Mức độ: {self.get_muc_do_display()}, Lý do: {self.ly_do}, "
              f"Người tạo: {nguoi_tao_info}, "
              f"Người duyệt: {nguoi_duyet_info}, "
              f"Trạng thái: {self.get_trang_thai_display()}, "
              f"Ngày tạo: {self.so_tien}{minh_chung}")




class KhenThuong(models.Model):
  TRANG_THAI_CHOICES = (
      ('DANG_CHO_DUYET', 'Đang chờ duyệt'),
      ('DA_DUYET', 'Đã duyệt'),
      ('DA_TU_CHOI', 'Đã từ chối'),
  )
  ngay_tao = models.DateTimeField(auto_now_add=True)
  nhan_vien = models.ForeignKey('NhanVien', on_delete=models.CASCADE, related_name='khen_thuong_nhan_vien')
  gia_tri = models.DecimalField(max_digits=10, decimal_places=2)
  ly_do = models.TextField()
  nguoi_tao_don = models.ForeignKey('NhanVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='khen_thuong_tao')
  nguoi_xac_nhan = models.ForeignKey('NhanVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='khen_thuong_xac_nhan')
  trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='DANG_CHO_DUYET')
  minh_chung_file = models.FileField(upload_to='minh_chung_khen_thuong/', null=True, blank=True)
  minh_chung_url = models.URLField(max_length=200, null=True, blank=True)


  def get_all_info(self):
      minh_chung = f", Minh chứng: {self.minh_chung_file.url if self.minh_chung_file else self.minh_chung_url if self.minh_chung_url else 'Không có'}"
      nguoi_tao_info = f"{self.nguoi_tao_don.ten_nv} ({self.nguoi_tao_don.chuc_vu})" if self.nguoi_tao_don else 'N/A'
      nguoi_xac_nhan_info = f"{self.nguoi_xac_nhan.ten_nv} ({self.nguoi_xac_nhan.chuc_vu})" if self.nguoi_xac_nhan else 'N/A'
      return (f"Tên NV: {self.nhan_vien.ten_nv}, Ngày tạo: {self.ngay_tao}, "
              f"Giá trị: {self.gia_tri}, Lý do: {self.ly_do}, "
              f"Người tạo: {nguoi_tao_info}, "
              f"Người xác nhận: {nguoi_xac_nhan_info}, "
              f"Trạng thái: {self.get_trang_thai_display()}{minh_chung}")






class ChamCong(models.Model):
  TRANG_THAI_CHOICES = [
      (0, "Đúng giờ"),
      (1, "Nghỉ"),
      (2, "Muộn"),
  ]
  nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
  gio_vao = models.TimeField(null=True, blank=True, verbose_name="Giờ Vào")
  gio_ra = models.TimeField(null=True, blank=True, verbose_name="Giờ Ra")
  ngay = models.IntegerField(verbose_name="Ngày")
  thang = models.IntegerField(verbose_name="Tháng")
  nam = models.IntegerField(verbose_name="Năm")
  trang_thai = models.IntegerField(choices=TRANG_THAI_CHOICES, verbose_name="Trạng Thái")




  class Meta:
      unique_together = ("nhan_vien", "ngay", "thang", "nam")  # Đảm bảo mỗi nhân viên chỉ có một bản ghi mỗi ngày
      ordering = ["nam", "thang", "ngay"]




  def __str__(self):
      return f"Nhân viên {self.nhan_vien} - {self.ngay}/{self.thang}/{self.nam} - {self.get_trang_thai_display()}"


def datetime():
    return None