from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from HOME.models import NhanVien, HopDongLaoDong


def hoso(request, id): #admin
    nhan_vien = get_object_or_404(NhanVien, id=id)

    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()

    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
    }

    return render(request, 'HoSo/hosochitiet.html', context)



def danh_sach_nhan_vien(request):
    nhan_vien_list = NhanVien.objects.all()

    context = {
        'nhan_vien_list': nhan_vien_list,
    }
    return render(request, 'HoSo/danhsachnhanvien.html', context)


def them_moi_ho_so(request):
    if request.method == "POST":
        ten_nv = request.POST.get('ten_nv')
        so_cccd = request.POST.get('so_cccd')
        trinh_do_hoc_van = request.POST.get('trinh_do_hoc_van')
        vi_tri_cong_viec = request.POST.get('vi_tri_cong_viec')
        kinh_nghiem = request.POST.get('kinh_nghiem')
        ngay_sinh = request.POST.get('ngay_sinh')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        email = request.POST.get('email')
        dia_chi = request.POST.get('dia_chi')

        loai_hop_dong = request.POST.get('loai_hop_dong')
        thoi_han_hop_dong = request.POST.get('thoi_han_hop_dong')
        ngay_vao_lam = request.POST.get('ngay_vao_lam')
        muc_luong = request.POST.get('muc_luong')
        trang_thai_hop_dong = request.POST.get('trang_thai_hop_dong')

        nhan_vien = NhanVien.objects.create(
            ten_nv=ten_nv,
            so_cccd=so_cccd,
            trinh_do_hoc_van=trinh_do_hoc_van,
            vi_tri_cong_viec=vi_tri_cong_viec,
            kinh_nghiem_lam_viec=kinh_nghiem,
            ngay_sinh=ngay_sinh,
            so_dien_thoai=so_dien_thoai,
            email=email,
            dia_chi=dia_chi,
        )


        hop_dong = HopDongLaoDong.objects.create(
            nhan_vien=nhan_vien,
            loai_hop_dong=loai_hop_dong,
            thoi_han_hop_dong=thoi_han_hop_dong,
            ngay_vao_lam=ngay_vao_lam,
            muc_luong=muc_luong,
            trang_thai_hop_dong=trang_thai_hop_dong
        )

        return redirect('success')

    return render(request, 'HoSo/Themmoihoso.html')


@login_required
def nv_hosochitiet(request): #user

    nhan_vien = get_object_or_404(NhanVien, user=request.user)
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()
    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
    }

    return render(request, 'HoSo/nv_hosochitiet.html', context)
