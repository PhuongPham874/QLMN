from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from HOME.models import NhanVien, HopDongLaoDong, PhuCapNhanVien
from datetime import datetime
from django.contrib.auth.models import User



# Hiển thị thông tin hợp đồng lao động và phụ cấp của nhân viên
def hosochitietHDLD(request, nhan_vien_id):
    nhan_vien = get_object_or_404(NhanVien, id=nhan_vien_id)
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()

    # Kiểm tra nếu không có hợp đồng lao động, chuyển hướng hoặc hiển thị thông báo lỗi
    if not hop_dong:
        return redirect('error_page')  # hoặc hiển thị thông báo lỗi nếu cần

    phu_cap_nhan_vien_list = PhuCapNhanVien.objects.filter(nhan_vien=nhan_vien)
    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
        'phu_cap_nhan_vien_list': phu_cap_nhan_vien_list,
    }
    return render(request, 'HoSo/hosochitietHDLD.html', context)

# Hiển thị thông tin cá nhân của nhân viên
def hosochitiet(request, id):
    nhan_vien = get_object_or_404(NhanVien, id=id)

    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()  # Kiểm tra xem có hợp đồng lao động không
    context = {'nhan_vien': nhan_vien, 'hop_dong': hop_dong}

    return render(request, 'HoSo/hosochitiet.html', context)

def danh_sach_nhan_vien(request):
    nhan_vien_list = NhanVien.objects.all()
    context = {
        'nhan_vien_list': nhan_vien_list,
    }
    return render(request, 'HoSo/danhsachnhanvien.html', context)






from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NhanVienForm, HopDongLaoDongForm
from HOME.models import NhanVien, User


def them_moi_ho_so(request):
    if request.method == "POST":
        form = NhanVienForm(request.POST, request.FILES)
        # Kiểm tra xem form có hợp lệ không
        if form.is_valid():
            # Lấy dữ liệu từ form
            # Lưu nhân viên mới
            nhan_vien = form.save(commit=False)
            # Tạo User mới (nếu cần) từ email (hoặc thông tin khác)
            user = User.objects.create_user(
                username=nhan_vien.email.split('@')[0],  # Tạo username từ email (bạn có thể tùy chỉnh)
                email=nhan_vien.email,
                password="defaultpassword"  # Có thể sử dụng password mặc định hoặc yêu cầu người dùng nhập
            )
            # Gán User cho nhân viên
            nhan_vien.user = user
            nhan_vien.save()
            # Sau khi lưu thành công, chuyển hướng về danh sách nhân viên
            return redirect('themmoi_hdld', nhan_vien_id=nhan_vien.id)
        else:
            # Nếu form không hợp lệ, in ra lỗi để kiểm tra
            print(form.errors)
    else:
        # Nếu phương thức GET, tạo form trống
        form = NhanVienForm()

    # Trả về template để hiển thị form
    return render(request, 'HoSo/ThemMoiHoSo.html', {'form': form})


def them_moi_hop_dong(request, nhan_vien_id):
    nhan_vien = NhanVien.objects.get(id=nhan_vien_id)
    form = HopDongLaoDongForm(request.POST or None, request.FILES or None, nhan_vien=nhan_vien)

    if form.is_valid():
        hopdong = form.save(commit=False)
        hopdong.nhan_vien = nhan_vien
        hopdong.vi_tri_lam_viec = nhan_vien.vi_tri_cong_viec
        hopdong.to_phong_ban = nhan_vien.to_phong_ban
        hopdong.save()
        return redirect('DanhSachNhanVien')  # Chuyển hướng sau khi lưu hợp đồng
    else:
        # Nếu form không hợp lệ, in ra lỗi để kiểm tra
        print(form.errors)
    return render(request, 'HoSo/ThemMoiHoSo_HDLD.html', {'form': form, 'nhan_vien': nhan_vien})


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
    # Lấy nhân viên từ cơ sở dữ liệu theo người dùng hiện tại
    nhan_vien = get_object_or_404(NhanVien, user=request.user)

    # Lấy hợp đồng lao động của nhân viên
    hop_dong = HopDongLaoDong.objects.filter(nhan_vien=nhan_vien).first()

    # Lấy danh sách phụ cấp của nhân viên
    phu_cap_nhan_vien_list = PhuCapNhanVien.objects.filter(nhan_vien=nhan_vien)

    # Truyền thông tin nhân viên, hợp đồng và phụ cấp vào context
    context = {
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
        'phu_cap_nhan_vien_list': phu_cap_nhan_vien_list,
    }

    # Render trang chi tiết nhân viên với context
    return render(request, 'HoSo/nv_hosochitietHDLD.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from HOME.models import NhanVien
from .forms import NhanVienForm

# Chỉnh sửa hồ sơ nhân viên
def edit_ho_so(request, id):
    # Lấy nhân viên theo ID
    nhan_vien = get_object_or_404(NhanVien, id=id)

    # Nếu là POST request, nghĩa là người dùng đã nhấn Lưu
    if request.method == 'POST':
        form = NhanVienForm(request.POST, request.FILES, instance=nhan_vien)

        # Kiểm tra tính hợp lệ của form
        if form.is_valid():
            form.save()  # Lưu thông tin vào cơ sở dữ liệu
            return redirect('QLXemHoSo', id=nhan_vien.id)  # Chuyển hướng đến trang xem hồ sơ chi tiết

        else:
            print("Form không hợp lệ")
            print(form.errors)  # Xem các lỗi của form để debug

    else:
        form = NhanVienForm(instance=nhan_vien)

    # Render lại trang với form
    return render(request, 'HoSo/edit_ho_so.html', {'form': form, 'nhan_vien': nhan_vien})