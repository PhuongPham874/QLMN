from django.contrib.auth.decorators import login_required
from django.core.management.commands.runserver import naiveip_re
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from HOME.models import BHXH,NhanVien,HopDongLaoDong,DONGBHXH
from .forms import *
def tinh_tong_tien_bhxh(nhan_vien, nhan_vien_dong, truong_dong):
    hop_dong = HopDongLaoDong.objects.get(nhan_vien=nhan_vien)
    muc_luong = hop_dong.luong
        # Tính tổng tiền BHXH: (nhân viên đóng + trường đóng) * mức lương
    tong_tien = ((nhan_vien_dong / 100) * muc_luong) + ((truong_dong / 100) * muc_luong)
    return tong_tien

def bhxh(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    bhxh_list = BHXH.objects.all()  # Lấy tất cả các đối tượng BHXH
    return render(request, 'BHXH/BHXH.html', {'bhxh_list': bhxh_list, 'nhan_vien':nhanvien })

def themmoiBHXH(request):
    # Lấy danh sách nhân viên chưa có BHXH
    nhan_vien_choices = NhanVien.objects.filter(
        id__in=[nv.id for nv in NhanVien.objects.all() if not BHXH.objects.filter(nhan_vien=nv).exists()]
    )
    if request.method == 'POST':
        form = BHXHform(request.POST)
        form.fields['ten_nv'].queryset = nhan_vien_choices
        if form.is_valid():
            nhan_vien = form.cleaned_data['ten_nv']
            hopdong = HopDongLaoDong.objects.filter(
                nhan_vien=nhan_vien,
                loai_hop_dong='Hợp đồng có thời hạn',
                trang_thai_hop_dong='Đang hiệu lực'
            ).first()
            if not hopdong:
                messages.error(request, "Không có thông tin BHXH của nhân viên này")
                return render(request, 'ThemBHXH.html', {'form': form})
            # Nếu có hợp đồng phù hợp, lưu form
            instance = form.save(commit=False)
            instance.nhan_vien = nhan_vien
            instance.save()
            messages.success(request, "Thêm mới BHXH thành công!")
            return redirect('bhxh_list')
    else:
        form = BHXHform()
        form.fields['ten_nv'].queryset = nhan_vien_choices
    return render(request, 'BHXH/ThemBHXH.html', {'form': form})
def chinhsuaBHXH(request, ma_nv):
    bhxh = get_object_or_404(BHXH, nhan_vien_id=ma_nv)
    if request.method == 'POST':
        form = updateBHXH(request.POST, instance=bhxh)
        if form.is_valid():
            form.save()  # Lưu thông tin vào cơ sở dữ liệu
            messages.success(request, "Chỉnh sửa thông tin thành công")
            return redirect('bhxh_list')
        else:
            print("Form is invalid")
            print(form.errors)
    else:
        form = updateBHXH(instance=bhxh)
    return render(request, "ChinhsuaBHXH.html", {"form": form,"bhxh": bhxh})
def thongtinchitiet(request,ma_nv):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    nhan_vien_obj = get_object_or_404(NhanVien, id=ma_nv)
    bhxhchitiet = BHXH.objects.get(nhan_vien = nhan_vien_obj)
    dongbhchitiet = DONGBHXH.objects.filter(nhan_vien = nhan_vien_obj)
    so_lan_tham_gia = dongbhchitiet.count()
    Total=0
    for dong in dongbhchitiet:
        Total += dong.tong_tien
    context = {'bh':bhxhchitiet,'dongbh':dongbhchitiet,'Total':Total,'solanthamgia':so_lan_tham_gia, 'nhan_vien': nhanvien}
    return render(request,'BHXH/Hienthichitiet.html',context)
def dong_bhxh(request):
    if request.method == "POST":
        form = DongBHXHForm(request.POST)
        if form.is_valid():
            ngay_bat_dau = form.cleaned_data['ngay_bat_dau']
            ngay_ket_thuc = form.cleaned_data['ngay_ket_thuc']
            bhxh_list = BHXH.objects.select_related('nhan_vien')  # Lấy danh sách BHXH với liên kết nhân viên
            created_count = 0
            for bhxh in bhxh_list:
                nhan_vien = bhxh.nhan_vien
                tong_tien = tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong)
                # Tạo bản ghi mới và lưu
                dong = DONGBHXH(
                    nhan_vien=nhan_vien,
                    ngay_bat_dau=ngay_bat_dau,
                    ngay_ket_thuc=ngay_ket_thuc,
                    tong_tien=tong_tien
                )
                dong.save()
                created_count += 1
            messages.success(request, f'Đã nộp tiền BHXH cho {created_count} nhân viên.')
            return redirect('bhxh_list')
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc.')
    else:
        form = DongBHXHForm()
    return render(request, 'BHXH/Noptien.html', {'form': form})


@login_required
def redirect_bhxh_view(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    if nhanvien.chuc_vu in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng']:
        return redirect('bhxh_list')
    else:
        return redirect('info_bhxh',ma_nv=nhanvien.id)


