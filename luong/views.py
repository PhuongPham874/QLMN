from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from HOME.models import NhanVien, ChamCong, HopDongLaoDong, PhuCap, BHXH, KhenThuong, KyLuat, PhuCapNhanVien
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib.auth.decorators import (login_required,permission_required)


def bang_luong_thang(request, nhan_vien_id, thang, nam):

    nhan_vien = get_object_or_404(NhanVien, id=nhan_vien_id)
    title = f"Bảng lương tháng {thang}/{nam}"


    cham_cong = ChamCong.objects.filter(nhan_vien=nhan_vien, thang=thang, nam=nam)
    so_ngay_lam = cham_cong.count()
    so_ngay_vang = cham_cong.filter(trang_thai=1).count()



    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).last()
    muc_luong = hop_dong.luong if hop_dong else Decimal('0')


    phu_cap_ids = PhuCapNhanVien.objects.filter(nhan_vien_id=nhan_vien_id).values_list('phu_cap_id', flat=True)
    tong_phu_cap = PhuCap.objects.filter(id__in=phu_cap_ids).aggregate(tong=Sum('gia_tri'))['tong'] or Decimal('0')


    vang_tru = (muc_luong / so_ngay_lam) * so_ngay_vang

    muon_tru = Decimal('0')  # Khởi tạo giá trị trừ lương do đi muộn
    for cham in cham_cong:
        if cham.trang_thai == 2:  # Trạng thái đi muộn
            if cham.gio_vao and cham.gio_vao.minute <= 10:
                muon_tru += Decimal('10000')  # Trừ 10k nếu muộn từ 1-10 phút
            elif cham.gio_vao and cham.gio_vao.minute <= 60:
                muon_tru += Decimal('100000')  # Trừ 100k nếu muộn từ 10 phút đến 1 giờ
            else:
                # Trừ 1/2 lương cơ bản nếu muộn hơn 1 giờ
                muon_tru += muc_luong / Decimal('2') / Decimal(so_ngay_lam)


    phu_cap_chuyen_can = Decimal('500000') if so_ngay_lam >= 18 else Decimal('0')

    khenthuong = KhenThuong.objects.filter(nhan_vien=nhan_vien, ngay_tao__year=nam, ngay_tao__month=thang)
    so_khen_thuong = khenthuong.count()
    thuong = so_khen_thuong * Decimal('100000')

    kyluat_phat_tien = KyLuat.objects.filter(
        nhan_vien=nhan_vien,
        muc_do='PHAT_TIEN',
        ngay_bat_dau__month=thang,
        ngay_bat_dau__year=nam,  # nên lọc thêm theo năm
        trang_thai='DA_DUYET'  # chỉ tính những cái đã duyệt
    )


    tien_ky_luat = kyluat_phat_tien.aggregate(total=Sum('so_tien_phat'))['total'] or Decimal('0')

    tien_bhxh = Decimal('0')
    bhxh = BHXH.objects.filter(nhan_vien=nhan_vien).last()
    if bhxh:
        tien_bhxh = (bhxh.nhan_vien_dong / 100) * muc_luong


    thue = Decimal('0.005') * muc_luong

    # Tổng lương sau khi cộng phụ cấp và trừ các khoản
    tong_luong = muc_luong - tien_bhxh - thue - tien_ky_luat + thuong - muon_tru - vang_tru + phu_cap_chuyen_can + tong_phu_cap

    # Chuẩn bị dữ liệu cho bảng lương
    bang_luong = {
        'nhan_vien': nhan_vien,
        'title': title,
        'muc_luong': muc_luong,
        'thuong': thuong,
        'tien_ky_luat': tien_ky_luat,
        'thue': thue,
        'muon_tru': muon_tru,
        'vang_tru': vang_tru,
        'phu_cap_chuyen_can': phu_cap_chuyen_can,
        'tien_bhxh': tien_bhxh,
        'tong_phu_cap': tong_phu_cap,
        'tong_luong': tong_luong,
        'thang': thang,
        'nam': nam,
    }
    return bang_luong

@login_required
def chuyen_huong_luong(request):
    nhan_vien = get_object_or_404(NhanVien, user=request.user)

    if nhan_vien.vi_tri_cong_viec == 'Kế toán':
        return redirect('danh_sach_nhan_vien')
    else:
        return redirect('xem_bang_luong_cua_toi')

@login_required
def xem_bang_luong_cua_toi(request):
    try:
        nhan_vien = get_object_or_404(NhanVien, user=request.user)
    except NhanVien.DoesNotExist:
        return render(request, 'error.html', {'message': 'Không tìm thấy nhân viên liên kết với tài khoản này.'})

    # Lấy tất cả các tháng và năm đã có bảng chấm công
    cham_cong = ChamCong.objects.filter(nhan_vien=nhan_vien)
    months_and_years = cham_cong.values_list('thang', 'nam').distinct()
    cham_cong_data = ChamCong.objects.filter(nhan_vien=nhan_vien)

    cham_cong_theo_thang = {}
    all_months = set()
    all_years = set()

    for record in cham_cong_data:
        year = record.nam
        month = record.thang
        day = record.ngay

        year_month = f"{year}-{month:02d}"
        if year_month not in cham_cong_theo_thang:
            cham_cong_theo_thang[year_month] = {}
        cham_cong_theo_thang[year_month][day] = record

        all_months.add(month)
        all_years.add(year)

    years = sorted(all_years)

    # Khởi tạo danh sách bảng lương
    bang_luong_list = []
    processed_months = set()

    for month, year in months_and_years:
        month_year_key = f"{month}-{year}"
        if month_year_key not in processed_months:
            bang_luong = bang_luong_thang(request, nhan_vien.id, month, year)
            bang_luong_list.append(bang_luong)
            processed_months.add(month_year_key)

    # Sắp xếp bảng lương từ tháng gần nhất
    bang_luong_list.sort(key=lambda x: x['title'], reverse=True)

    return render(request, 'Luong/danh_sach_luong.html', {
        'bang_luong_list': bang_luong_list,
        'nhan_vien': nhan_vien,
        'years' : years
    })
@login_required
@permission_required('KeToan')
def danh_sach_nhan_vien_va_luong(request):
    nhan_vien = get_object_or_404(NhanVien, user=request.user)
    if nhan_vien.vi_tri_cong_viec not in ['Kế toán']:
        return render(request, 'error.html', {'message': 'Bạn không có quyền truy cập vào phần này.'})

    nhan_viens = NhanVien.objects.all().order_by('id')

    return render(request, 'Luong/Danh_sach_nhan_vien.html', {
        'user': request.user,
        'nhan_viens': nhan_viens,
        'nhan_vien': nhan_vien
    })

@login_required
def xem_bang_luong_cua_nhan_vien(request, nhan_vien_id):
    nhan_vien = get_object_or_404(NhanVien, id=nhan_vien_id)
    cham_cong_data = ChamCong.objects.filter(nhan_vien=nhan_vien)

    cham_cong_theo_thang = {}
    all_months = set()
    all_years = set()

    for record in cham_cong_data:
        year = record.nam
        month = record.thang
        day = record.ngay

        year_month = f"{year}-{month:02d}"
        if year_month not in cham_cong_theo_thang:
            cham_cong_theo_thang[year_month] = {}
        cham_cong_theo_thang[year_month][day] = record

        all_months.add(month)
        all_years.add(year)

    years = sorted(all_years)
    # Lấy tất cả các tháng và năm đã có bảng chấm công của nhân viên
    cham_cong = ChamCong.objects.filter(nhan_vien=nhan_vien)
    months_and_years = cham_cong.values_list('thang', 'nam').distinct()

    # Khởi tạo danh sách bảng lương
    bang_luong_list = []
    processed_months = set()

    for month, year in months_and_years:
        month_year_key = f"{month}-{year}"
        if month_year_key not in processed_months:
            bang_luong = bang_luong_thang(request, nhan_vien.id, month, year)
            bang_luong_list.append(bang_luong)
            processed_months.add(month_year_key)

    # Sắp xếp bảng lương từ tháng gần nhất
    bang_luong_list.sort(key=lambda x: x['title'], reverse=True)

    return render(request, 'Luong/danh_sach_luong.html', {
        'bang_luong_list': bang_luong_list,
        'nhan_vien': nhan_vien,
        'years': years
    })

