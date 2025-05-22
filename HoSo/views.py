from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from HOME.models import NhanVien, HopDongLaoDong, PhuCapNhanVien, User, PhuCap
from datetime import datetime
from django.contrib.auth.models import User
from .forms import NhanVienForm, HopDongLaoDongForm



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
    context = {
        'nhan_vien': nhan_vien, 'hop_dong': hop_dong
    }

    return render(request, 'HoSo/hosochitiet.html', context)
'''
def danh_sach_nhan_vien(request):
    nhan_vien_list = NhanVien.objects.all()
    context = {
        'nhan_vien_list': nhan_vien_list,
    }
    return render(request, 'HoSo/danhsachnhanvien.html', context)
'''



def danh_sach_nhan_vien(request):
    query = request.GET.get('q', '')  # Lấy giá trị tìm kiếm từ thanh tìm kiếm
    if query:
        nhan_vien_list = NhanVien.objects.filter(ten_nv__icontains=query)  # Lọc nhân viên theo tên
    else:
        nhan_vien_list = NhanVien.objects.all()  # Nếu không có tìm kiếm, hiển thị tất cả nhân viên

    return render(request, 'HoSo/danhsachnhanvien.html', {
        'nhan_vien_list': nhan_vien_list,
        'query': query
    })


def Add_ho_so(request):
    form = NhanVienForm(request.POST, request.FILES)
    if request.method == 'POST':
        # Kiểm tra xem form có hợp lệ không
        if form.is_valid():
            # Lưu nhân viên mới
            nhan_vien = form.save(commit=False)
                # Lấy dữ liệu từ form
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
            # Truyền lỗi form xuống template để hiển thị
            messages.error(request, "Vui lòng nhập ")
    else:
        form = NhanVienForm()

    # Trả về template để hiển thị form
    return render(request, 'HoSo/ThemMoiHoSo.html', {'form': form})


def them_moi_hop_dong(request, nhan_vien_id):
    nhan_vien = NhanVien.objects.get(id=nhan_vien_id)
    form = HopDongLaoDongForm(request.POST or None, request.FILES or None, nhan_vien=nhan_vien)
    danh_sach_phu_cap = PhuCap.objects.all()
    phu_cap_da_chon = PhuCapNhanVien.objects.filter(nhan_vien=nhan_vien).values_list('phu_cap_id', flat=True)

    selected_ids = request.POST.getlist('phu_cap_ids')
    if request.method == 'POST':
        if form.is_valid():
            hopdong = form.save(commit=False)
            hopdong.nhan_vien = nhan_vien
            hopdong.vi_tri_lam_viec = nhan_vien.vi_tri_cong_viec
            hopdong.to_phong_ban = nhan_vien.to_phong_ban



            hopdong.save()

            for phu_cap_id in selected_ids:
                phu_cap_obj = PhuCap.objects.get(id=phu_cap_id)
                PhuCapNhanVien.objects.create(nhan_vien=nhan_vien, phu_cap=phu_cap_obj)

            return redirect('DanhSachNhanVien')  # Chuyển hướng sau khi lưu hợp đồng
        else:
            # Nếu form không hợp lệ, in ra lỗi để kiểm tra
            print(form.errors)
    else:
        form = HopDongLaoDongForm()
    return render(request, 'HoSo/ThemMoiHoSo_HDLD.html', {'form': form, 'nhan_vien': nhan_vien, 'danh_sach_phu_cap': danh_sach_phu_cap,})


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
            print(form.errors)  # Xem các lỗi của form để debu
    else:
        form = NhanVienForm(instance=nhan_vien)

    # Render lại trang với form
    return render(request, 'HoSo/edit_ho_so.html', {'form': form, 'nhan_vien': nhan_vien})


from django.shortcuts import render, redirect, get_object_or_404
from HOME.models import NhanVien, HopDongLaoDong
from .forms import HopDongLaoDongForm  # Form chỉnh sửa hợp đồng lao động (nếu chưa có)

def edit_hdld(request, nhan_vien_id):
    # Lấy thông tin nhân viên và hợp đồng lao động của nhân viên đó
    nhan_vien = get_object_or_404(NhanVien, id=nhan_vien_id)
    hop_dong = get_object_or_404(HopDongLaoDong, nhan_vien=nhan_vien)
    danh_sach_phu_cap = PhuCap.objects.all()
    phu_cap_da_chon = PhuCapNhanVien.objects.filter(nhan_vien=nhan_vien).values_list('phu_cap_id', flat=True)
    # Kiểm tra nếu yêu cầu là POST (lưu thông tin)
    if request.method == "POST":
        form = HopDongLaoDongForm(request.POST, instance=hop_dong)

        # Kiểm tra form hợp lệ
        if form.is_valid():
            selected_ids = request.POST.getlist('phu_cap_ids')
            PhuCapNhanVien.objects.filter(nhan_vien=nhan_vien).delete()
            for phu_cap_id in selected_ids:
                phu_cap_obj = PhuCap.objects.get(id=phu_cap_id)
                PhuCapNhanVien.objects.create(nhan_vien=nhan_vien, phu_cap=phu_cap_obj)
            form.save()  # Lưu thông tin hợp đồng vào cơ sở dữ liệu
            return redirect('QLXemHoSoHDLD', nhan_vien_id=nhan_vien.id)  # Quay lại trang xem hợp đồng

    else:
        # Tạo form với dữ liệu hiện tại của hợp đồng lao động
        form = HopDongLaoDongForm(instance=hop_dong)

    return render(request, 'HoSo/edit_hdld.html', {
        'form': form,
        'nhan_vien': nhan_vien,
        'hop_dong': hop_dong,
        'phu_cap_da_chon': list(phu_cap_da_chon),
        'danh_sach_phu_cap': danh_sach_phu_cap
    })


@login_required
def redirect_hoso_view(request):
    user = get_object_or_404(NhanVien, user=request.user)
    if user.vi_tri_cong_viec in [ 'Nhân sự', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Hiệu Trưởng']:
        return redirect('DanhSachNhanVien')
    else:
        return redirect('NVXemHoSo')