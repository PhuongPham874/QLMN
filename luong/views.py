from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from HOME.models import HopDongLaoDong, KhenThuong, KyLuat, ChamCong, NghiPhep, NhanVien,BHXH
from decimal import Decimal
from collections import defaultdict

@login_required
def bang_luong_thang(request, month, year):
    # Lấy thông tin nhân viên của người dùng hiện tại
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)  # Lấy nhân viên liên kết với User
    except NhanVien.DoesNotExist:
        return render(request, 'error.html', {'message': 'Không tìm thấy nhân viên liên kết với tài khoản này.'})

    # Lấy hợp đồng lao động của nhân viên
    hopdong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()
    if not hopdong:
        return render(request, 'error.html', {'message': 'Không tìm thấy hợp đồng lao động.'})

    muc_luong = hopdong.muc_luong  # Lấy lương cơ bản từ hợp đồng lao động

    bhxh = BHXH.objects.filter(nhan_vien=nhan_vien).first()
    nhan_vien_dong = Decimal('0')
    tien_bhxh = Decimal('0')

    if bhxh:
        nhan_vien_dong = bhxh.nhan_vien_dong or Decimal('0')
        tien_bhxh = muc_luong * nhan_vien_dong / Decimal('100')

    # Lấy tất cả các bản ghi chấm công của nhân viên trong tháng và năm
    cham_cong = ChamCong.objects.filter(nhan_vien=nhan_vien, ngay__month=month, ngay__year=year)

    # Thuế = 0.5% lương cơ bản
    thue = muc_luong * Decimal('0.005')

    # Lọc kỷ luật theo tháng và năm
    ky_luat = KyLuat.objects.filter(nhan_vien=nhan_vien, ngay_bat_dau__month=month, ngay_bat_dau__year=year)
    phat_tien = ky_luat.filter(muc_do="Phạt tiền").exists()
    if phat_tien:
        muc_luong -= Decimal('100000')  # Trừ 100k nếu có phạt tiền

    # Lọc thưởng theo tháng và năm
    thuong = Decimal(KhenThuong.objects.filter(nhan_vien=nhan_vien, ngay_khen_thuong__month=month, ngay_khen_thuong__year=year)
                     .aggregate(Sum('gia_tri'))['gia_tri__sum'] or 0)

    # Lọc nghỉ phép theo tháng và năm
    nghi_phep = NghiPhep.objects.filter(nhan_vien=nhan_vien, ngay_bat_dau__month=month, ngay_bat_dau__year=year)

    # Tính tổng số ngày làm việc đúng giờ
    tong_so_ngay = cham_cong.filter(trang_thai=0).count()  # Số ngày đi làm đúng giờ

    # Tính đi muộn
    muon_tru = Decimal('0')  # Khởi tạo giá trị trừ lương do đi muộn
    for cham in cham_cong:
        if cham.trang_thai == 2:  # Trạng thái đi muộn
            if cham.gio_vao and cham.gio_vao.minute <= 10:
                muon_tru += Decimal('10000')  # Trừ 10k nếu muộn từ 1-10 phút
            elif cham.gio_vao and cham.gio_vao.minute <= 60:
                muon_tru += Decimal('100000')  # Trừ 100k nếu muộn từ 10 phút đến 1 giờ
            else:
                # Trừ 1/2 lương cơ bản nếu muộn hơn 1 giờ
                muon_tru += muc_luong / Decimal('2') / Decimal(tong_so_ngay)

    # Tính vắng mặt (nếu nghỉ không phép)
    vang_tru = Decimal('0')  # Khởi tạo giá trị trừ lương do vắng
    for cham in cham_cong:
        if cham.trang_thai == 1:  # Trạng thái nghỉ
            if not nghi_phep.filter(ngay_bat_dau=cham.ngay).exists():  # Nếu không có bản ghi nghỉ phép cho ngày đó
                vang_tru += muc_luong / Decimal(tong_so_ngay)  # Trừ theo tỷ lệ ngày vắng

    # Tính tổng lương cho tháng và năm hiện tại
    tong_luong = muc_luong + thuong - thue - muon_tru - vang_tru - tien_bhxh

    # Tạo title cho bảng lương
    title = f"Tháng {month}/{year}"

    # Gom các thông tin vào 1 dictionary cho bảng lương
    bang_luong = {
        'nhan_vien': nhan_vien,
        'title': title,
        'muc_luong': muc_luong,
        'thuong': thuong,
        'thue': thue,
        'muon_tru': muon_tru,
        'vang_tru': vang_tru,
        'tien_bhxh': tien_bhxh,
        'tong_luong': tong_luong,
    }

    return bang_luong
@login_required
def danh_sach_luong(request):
    # Lấy thông tin nhân viên của người dùng hiện tại
    try:
        nhan_vien = request.user.nhanvien  # Lấy nhân viên liên kết với User
    except NhanVien.DoesNotExist:
        return render(request, 'error.html', {'message': 'Không tìm thấy nhân viên liên kết với tài khoản này.'})

    # Lấy tất cả các tháng và năm đã có bảng chấm công
    cham_cong = ChamCong.objects.filter(nhan_vien=nhan_vien)
    months_and_years = cham_cong.values('ngay__month', 'ngay__year').distinct()

    # Khởi tạo danh sách bảng lương và set để lưu các tháng và năm đã xuất hiện
    bang_luong_list = []
    seen_months_and_years = set()  # Set để lưu các tháng và năm đã thấy

    for month_year in months_and_years:
        month = month_year['ngay__month']
        year = month_year['ngay__year']
        # Kiểm tra nếu tháng và năm đã xuất hiện, nếu chưa thì thêm vào bang_luong_list
        if (month, year) not in seen_months_and_years:
            # Gọi hàm bang_luong_thang để lấy thông tin bảng lương cho tháng và năm
            bang_luong = bang_luong_thang(request, month, year)
            bang_luong_list.append(bang_luong)
            seen_months_and_years.add((month, year))  # Thêm tháng và năm vào set để tránh trùng

    # Sắp xếp bảng lương từ tháng gần nhất
    bang_luong_list.sort(key=lambda x: (x['title']), reverse=True)

    return render(request, 'Luong/danh_sach_luong.html', {
        'bang_luong_list': bang_luong_list,
        'nhan_vien' : nhan_vien
    })

