from django.shortcuts import render,redirect,get_object_or_404
from HOME.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def tinh_tong_tien_bhxh(nhan_vien, nhan_vien_dong, truong_dong):
    hop_dong = HopDongLaoDong.objects.get(nhan_vien=nhan_vien)
    muc_luong = hop_dong.muc_luong  # Lấy mức lương từ hợp đồng
        # Tính tổng tiền BHXH: (nhân viên đóng + trường đóng) * mức lương
    tong_tien = ((nhan_vien_dong / 100) * muc_luong) + ((truong_dong / 100) * muc_luong)
    return tong_tien

def bhxh(request):
    bhxh_list = BHXH.objects.all()  # Lấy tất cả các đối tượng BHXH
    for bhxh in bhxh_list:
        for bhxh in bhxh_list:
            # Gọi hàm tính tổng tiền BHXH
            bhxh.tong_tien_bhxh = tinh_tong_tien_bhxh(bhxh.nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong)
    return render(request, 'BHXH/BHXH.html', {'bhxh_list': bhxh_list})

def chinhsuaBHXH(request, ma_nv):
    bhxh = get_object_or_404(BHXH, nhan_vien_id=ma_nv)
    bhxh.tong_tien_bhxh = tinh_tong_tien_bhxh(bhxh.nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong)
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        maBHXH = request.POST.get('maBHXH')
        ngayBatDauDong = request.POST.get('ngayBatDauDong')
        # Cập nhật thông tin
        bhxh.ma_bhxh = maBHXH
        bhxh.thoi_gian_bat_dau_dong = ngayBatDauDong
        bhxh.save()
        # Thông báo thành công
        messages.success(request, "Chỉnh sửa thông tin thành công")
        return redirect('bhxh_list')
    return render(request, 'BHXH/chinhsuatt.html', {'bhxh': bhxh,'ten_nhan_vien': bhxh.nhan_vien.ten_nv,'ma_nv': bhxh.nhan_vien_id,})

@login_required
def thong_tin_bhxh(request):
    nhan_vien = NhanVien.objects.get(user=request.user)  # Lấy nhân viên từ user đã đăng nhập
    try:
        bhxh = BHXH.objects.get(nhan_vien=nhan_vien)  # Tìm thông tin BHXH của nhân viên
    except BHXH.DoesNotExist:
        bhxh = None  # Nếu không có thông tin BHXH, trả về None
    return render(request, 'BHXH/ThongtinBHXHuser.html', {'bhxh': bhxh, 'nhan_vien': nhan_vien})

def themmoiBHXH(request):
    # Tạo danh sách nhân viên chưa có BHXH
    nhan_vien_choices = []
    all_nhan_vien = NhanVien.objects.all()
    for nhan_vien in all_nhan_vien:
        # Kiểm tra nếu nhân viên chưa có BHXH
        if not BHXH.objects.filter(nhan_vien=nhan_vien).exists():
            nhan_vien_choices.append(nhan_vien)
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        tenNhanVien = request.POST.get('tenNhanVien')
        maBHXH = request.POST.get('maBHXH')
        nhanVienDong = request.POST.get('nhanVienDong')
        truongDong = request.POST.get('truongDong')
        tongTienBHXH = request.POST.get('tongTienBHXH')
        ngayBatDauDong = request.POST.get('ngayBatDauDong')
        # Tìm nhân viên theo mã nhân viên được chọn
    return render(request, 'BHXH/themmoiBHXH.html', {'nhan_vien_choices': nhan_vien_choices}, )