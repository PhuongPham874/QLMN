from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from HOME.models import NhanVien, HopDongLaoDong


def hosochitiet(request, id):  # Admin - Hiển thị chi tiết hồ sơ nhân viên
    # Lấy nhân viên theo id
    nhan_vien = get_object_or_404(NhanVien, id=id)

    # Lấy thông tin hợp đồng lao động của nhân viên
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()

    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
    }

    return render(request, 'HoSo/hosochitiet.html', context)

def hosochitietHDLD(request, id):  # Admin - Hiển thị chi tiết hồ sơ nhân viên
    # Lấy nhân viên theo id
    nhan_vien = get_object_or_404(NhanVien, id=id)

    # Lấy thông tin hợp đồng lao động của nhân viên
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()

    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
    }

    return render(request, 'HoSo/hosochitietHDLD.html', context)


def danh_sach_nhan_vien(request):
    nhan_vien_list = NhanVien.objects.all()

    context = {
        'nhan_vien_list': nhan_vien_list,
    }
    return render(request, 'HoSo/danhsachnhanvien.html', context)


def them_moi_ho_so(request):
    if request.method == "POST":
        # Lấy dữ liệu từ form
        ten_nv = request.POST.get('ten_nv')
        anh_ca_nhan = request.FILES.get('anh_ca_nhan')  # Lấy ảnh từ form
        so_cccd = request.POST.get('so_cccd')
        gioi_tinh = request.POST.get('gioi_tinh')  # Lấy giới tính
        ngay_sinh = request.POST.get('ngay_sinh')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        email = request.POST.get('email')
        vi_tri_cong_viec = request.POST.get('vi_tri_cong_viec')
        to_phong_ban = request.POST.get('to_phong_ban')  # Lấy tổ phòng ban
        trinh_do_hoc_van = request.POST.get('trinh_do_hoc_van')
        chuyen_nganh = request.POST.get('chuyen_nganh')
        noi_dao_tao = request.POST.get('noi_dao_tao')
        nam_tn = request.POST.get('nam_tn')
        ngay_cap = request.POST.get('ngay_cap')
        noi_cap = request.POST.get('noi_cap')  # Nơi cấp
        dia_chi_tam_tru = request.POST.get('dia_chi_tam_tru')

        # Lấy thông tin hợp đồng lao động
        so_hop_dong = request.POST.get('so_hd')
        loai_hop_dong = request.POST.get('loai_hop_dong')
        thoi_han_hd = request.POST.get('thoi_han_hd')
        tu_ngay = request.POST.get('tu_ngay')
        den_ngay = request.POST.get('den_ngay')
        ngay_ky = request.POST.get('ngay_ky')
        trang_thai_hd = request.POST.get('trang_thai_hd')

        # Liên kết với người dùng đang đăng nhập
        user = request.user  # Sử dụng người dùng hiện tại đăng nhập

        # Tạo mới nhân viên
        nhan_vien = NhanVien.objects.create(
            user=user,  # Liên kết nhân viên với người dùng đang đăng nhập
            ten_nv=ten_nv,
            anh_ca_nhan=anh_ca_nhan,  # Lưu ảnh
            so_cccd=so_cccd,
            gioi_tinh=gioi_tinh,  # Lưu giới tính
            ngay_sinh=ngay_sinh,
            so_dien_thoai=so_dien_thoai,
            email=email,
            vi_tri_cong_viec=vi_tri_cong_viec,
            to_phong_ban=to_phong_ban,  # Lưu tổ phòng ban
            trinh_do_hoc_van=trinh_do_hoc_van,
            chuyen_nganh=chuyen_nganh,
            noi_dao_tao=noi_dao_tao,
            nam_tn=nam_tn,
            ngay_cap=ngay_cap,
            noi_cap=noi_cap,  # Nơi cấp
            dia_chi_tam_tru=dia_chi_tam_tru
        )

        # Tạo hợp đồng lao động
        hop_dong = HopDongLaoDong.objects.create(
            nhan_vien=nhan_vien,
            so_hop_dong=so_hop_dong,
            loai_hop_dong=loai_hop_dong,
            thoi_han_hop_dong=thoi_han_hd,
            tu_ngay=tu_ngay,
            den_ngay=den_ngay,
            ngay_ky=ngay_ky,
            trang_thai_hop_dong=trang_thai_hd
        )

        # Quay lại trang thành công hoặc trang khác
        return redirect('success')  # Chuyển hướng tới trang thành công hoặc trang cần thiết

    # Trả về form khi GET
    return render(request, 'HoSo/ThemMoiHoSo.html')


def them_moi_hop_dong(request):
    if request.method == "POST":
        # Lấy dữ liệu từ form
        ten_nv = request.POST.get('ten_nv')
        ma_nv = request.POST.get('ma_nv')
        vi_tri_cong_viec = request.POST.get('vi_tri_cong_viec')
        to_phong_ban = request.POST.get('to_phong_ban')  # Lấy tổ phòng ban

        # Thông tin hợp đồng lao động
        so_hop_dong = request.POST.get('so_hd')
        loai_hop_dong = request.POST.get('loai_hop_dong')
        thoi_han_hd = request.POST.get('thoi_han_hd')
        tu_ngay = request.POST.get('tu_ngay')
        den_ngay = request.POST.get('den_ngay')
        ngay_ky = request.POST.get('ngay_ky')
        trang_thai_hd = request.POST.get('trang_thai_hd')

        # Danh sách phụ cấp
        phu_cap_tham_nien = request.POST.get('phu_cap_tham_nien')
        phu_cap_di_lai = request.POST.get('phu_cap_di_lai')
        phu_cap_dung_lop = request.POST.get('phu_cap_dung_lop')

        # Giá trị phụ cấp
        gia_tri_phu_cap1 = request.POST.get('gia_tri_phu_cap1')
        gia_tri_phu_cap2 = request.POST.get('gia_tri_phu_cap2')
        gia_tri_phu_cap3 = request.POST.get('gia_tri_phu_cap3')

        # Liên kết với người dùng đang đăng nhập
        user = request.user  # Sử dụng người dùng hiện tại đăng nhập

        # Tạo mới nhân viên
        nhan_vien = NhanVien.objects.create(
            user=user,  # Liên kết nhân viên với người dùng đang đăng nhập
            ten_nv=ten_nv,
            ma_nv=ma_nv,
            vi_tri_cong_viec=vi_tri_cong_viec,
            to_phong_ban=to_phong_ban,  # Lưu tổ phòng ban
        )

        # Tạo hợp đồng lao động
        hop_dong = HopDongLaoDong.objects.create(
            nhan_vien=nhan_vien,
            so_hop_dong=so_hop_dong,
            loai_hop_dong=loai_hop_dong,
            thoi_han_hop_dong=thoi_han_hd,
            tu_ngay=tu_ngay,
            den_ngay=den_ngay,
            ngay_ky=ngay_ky,
            trang_thai_hop_dong=trang_thai_hd
        )

        # Nếu có phụ cấp, lưu chúng vào bảng phụ cấp
        if phu_cap_tham_nien:
            hop_dong.phu_caps.create(stt=1, ten_phu_cap="Phụ cấp thâm niên", gia_tri=gia_tri_phu_cap1)
        if phu_cap_di_lai:
            hop_dong.phu_caps.create(stt=2, ten_phu_cap="Phụ cấp đi lại", gia_tri=gia_tri_phu_cap2)
        if phu_cap_dung_lop:
            hop_dong.phu_caps.create(stt=3, ten_phu_cap="Phụ cấp đúng lớp", gia_tri=gia_tri_phu_cap3)

        # Quay lại trang thành công hoặc trang khác
        return redirect('success')  # Chuyển hướng tới trang thành công hoặc trang cần thiết

    # Trả về form khi GET
    return render(request, 'HoSo/ThemMoiHoSo_HĐLĐ.html')


@login_required
def nv_hosochitiet(request):
    # Lấy nhân viên từ cơ sở dữ liệu theo người dùng hiện tại
    nhan_vien = get_object_or_404(NhanVien, user=request.user)

    # Lấy hợp đồng lao động của nhân viên
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()

    # Truyền cả thông tin nhân viên và hợp đồng lao động vào context
    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
    }

    return render(request, 'HoSo/nv_hosochitiet.html', context)
@login_required
def nv_hosochitietHDLD(request):
    nhan_vien = get_object_or_404(NhanVien, user=request.user)
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()
    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
    }

    return render(request, 'HoSo/nv_hosochitietHDLD.html', context)



