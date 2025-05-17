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
# def bhxh(request):
#     nhanvien = get_object_or_404(NhanVien, user=request.user)
#     bhxh_list = BHXH.objects.all()  # Lấy tất cả các đối tượng BHXH
#     name_filter = request.GET.get('name', '')
#     if name_filter:
#         bhxh_list = bhxh_list.filter(nhan_vien__ten_nv__icontains=name_filter)
#     form = DongBHXHForm()
#     return render(request, 'BHXH/BHXH.html', {'bhxh_list': bhxh_list, 'nhan_vien':nhanvien,'name_filter': name_filter,'form': form,'tong_tien': 0 })
def bhxh(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    bhxh_list = BHXH.objects.all()

    # Lọc theo id nhân viên từ GET parameter
    nv_id = request.GET.get('nv_id')
    if nv_id:
        bhxh_list = bhxh_list.filter(nhan_vien__id=nv_id)

    # 👉 Lấy danh sách nhân viên có BHXH
    ds_nhanvien = NhanVien.objects.filter(id__in=bhxh_list.values_list('nhan_vien__id', flat=True))

    form = DongBHXHForm()
    return render(request, 'BHXH/BHXH.html', {
        'bhxh_list': bhxh_list,
        'nhan_vien': nhanvien,
        'ds_nhanvien': ds_nhanvien,  # ✅ Chỉ những nhân viên có BHXH
        'form': form,
        'selected_nv_id': nv_id if nv_id else '',
        'tong_tien': 0
    })


def themmoiBHXH(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
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
                return render(request, 'BHXH/ThemBHXH.html', {'form': form})
            # Nếu có hợp đồng phù hợp, lưu form
            instance = form.save(commit=False)
            instance.nhan_vien = nhan_vien
            instance.save()
            messages.success(request, "Thêm mới BHXH thành công!")
            return redirect('bhxh_list')
    else:
        form = BHXHform()
        form.fields['ten_nv'].queryset = nhan_vien_choices
    return render(request, 'BHXH/ThemBHXH.html', {'form': form, 'nhan_vien':nhanvien})

def chinhsuaBHXH(request, ma_nv):
    bhxh = get_object_or_404(BHXH, nhan_vien_id=ma_nv)
    if request.method == 'POST':
        form = updateBHXH(request.POST, instance=bhxh)
        if form.is_valid():
            form.save()  # Lưu thông tin vào cơ sở dữ liệu
            ten_nv = bhxh.nhan_vien.ten_nv
            messages.success(request, f"Chỉnh sửa thông tin BHXH của nhân viên {ten_nv} thành công")
            return redirect('bhxh_list')
        else:
            print("Form is invalid")
            print(form.errors)
    else:
        form = updateBHXH(instance=bhxh)
    return render(request, "BHXH/ChinhsuaBHXH.html", {"form": form,"bhxh": bhxh})

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

# def dong_bhxh(request):
#     if request.method == "POST":
#         form = DongBHXHForm(request.POST)
#         if form.is_valid():
#             ngay_bat_dau = form.cleaned_data['ngay_bat_dau']
#             ngay_ket_thuc = form.cleaned_data['ngay_ket_thuc']
#             bhxh_list = BHXH.objects.select_related('nhan_vien')  # Lấy danh sách BHXH với liên kết nhân viên
#             created_count = 0
#             for bhxh in bhxh_list:
#                 nhan_vien = bhxh.nhan_vien
#                 tong_tien = tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong)
#                 # Tạo bản ghi mới và lưu
#                 dong = DONGBHXH(
#                     nhan_vien=nhan_vien,
#                     ngay_bat_dau=ngay_bat_dau,
#                     ngay_ket_thuc=ngay_ket_thuc,
#                     tong_tien=tong_tien
#                 )
#                 dong.save()
#                 created_count += 1
#             messages.success(request, f'Đã nộp tiền BHXH cho {created_count} nhân viên.')
#             return redirect('bhxh_list')
#         else:
#             messages.error(request, 'Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc.')
#     else:
#         form = DongBHXHForm()
#     return redirect('bhxh_list')

# def dong_bhxh(request):
#     tong_tien_tat_ca = 0  # Biến cộng dồn tổng tiền
#     if request.method == "POST":
#         form = DongBHXHForm(request.POST)
#         if form.is_valid():
#             ngay_bat_dau = form.cleaned_data['ngay_bat_dau']
#             ngay_ket_thuc = form.cleaned_data['ngay_ket_thuc']
#             bhxh_list = BHXH.objects.select_related('nhan_vien')
#             created_count = 0
#             for bhxh in bhxh_list:
#                 nhan_vien = bhxh.nhan_vien
#                 tong_tien = tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong)
#                 dong = DONGBHXH(
#                     nhan_vien=nhan_vien,
#                     ngay_bat_dau=ngay_bat_dau,
#                     ngay_ket_thuc=ngay_ket_thuc,
#                     tong_tien=tong_tien
#                 )
#                 dong.save()
#                 created_count += 1
#                 tong_tien_tat_ca += int(tong_tien)  # Cộng dồn tổng tiền
#
#             messages.success(
#                 request,
#                 f'Đã nộp tiền BHXH cho {created_count} nhân viên, tổng số tiền: {tong_tien_tat_ca:,} VNĐ.'
#             )
#             return redirect('bhxh_list')
#         else:
#             messages.error(request, 'Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc.')
#     else:
#         form = DongBHXHForm()
#
#     # Truyền tong_tien_tat_ca vào context để sử dụng trong template
#     return render(request, 'BHXH/BHXH.html', {
#         'form': form,
#         'tong_tien': tong_tien_tat_ca

from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import datetime
from django.urls import reverse
@csrf_exempt
def tinh_tien_bhxh_ajax(request):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            ngay_bat_dau = request.POST.get('ngay_bat_dau')
            ngay_ket_thuc = request.POST.get('ngay_ket_thuc')
            # Chuyển định dạng ngày từ chuỗi sang đối tượng date
            ngay_bat_dau = datetime.datetime.strptime(ngay_bat_dau, '%Y-%m-%d').date()
            ngay_ket_thuc = datetime.datetime.strptime(ngay_ket_thuc, '%Y-%m-%d').date()
            # Kiểm tra 1: Ngày bắt đầu phải trước ngày kết thúc
            if ngay_bat_dau >= ngay_ket_thuc:
                return JsonResponse({'error': 'Ngày bắt đầu phải nhỏ hơn ngày kết thúc'}, status=400)
            # Kiểm tra 2: Kiểm tra khoảng thời gian trùng lặp trong cơ sở dữ liệu
            overlapping_payments = DONGBHXH.objects.filter(
                ngay_bat_dau__lte=ngay_ket_thuc,
                ngay_ket_thuc__gte=ngay_bat_dau
            )
            if overlapping_payments.exists():
                return JsonResponse({'error': 'Khoảng thời gian đã tồn tại trong cơ sở dữ liệu'}, status=400)
            # Tính tổng tiền nếu vượt qua các kiểm tra
            bhxh_list = BHXH.objects.select_related('nhan_vien')
            tong_tien_tat_ca = 0
            so_nguoi_dong_bhxh = 0
            for bhxh in bhxh_list:
                nhan_vien = bhxh.nhan_vien
                # Giả sử hàm tinh_tong_tien_bhxh đã được định nghĩa
                tong_tien = tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong)
                tong_tien_tat_ca += int(tong_tien)
                so_nguoi_dong_bhxh += 1
            # Kiểm tra nếu yêu cầu là lưu dữ liệu
            if 'submit' in request.POST:
                DONGBHXH.objects.create(
                    ngay_bat_dau=ngay_bat_dau,
                    ngay_ket_thuc=ngay_ket_thuc,
                    tong_tien=tong_tien_tat_ca,
                )
                # Thêm thông báo thành công
                message = f"Đã nộp BHXH cho {so_nguoi_dong_bhxh} người với tổng tiền là {tong_tien_tat_ca:,} VNĐ"

                return JsonResponse({
                    'message': message,
                    'tong_tien': tong_tien_tat_ca,
                    'so_nguoi_dong_bhxh': so_nguoi_dong_bhxh,
                })

            # Trả về JSON cho tính toán AJAX
            redirect_url = request.build_absolute_uri(reverse('bhxh_list'))
            print("🌐 Redirect URL (Server):", redirect_url)
            return JsonResponse({
                'tong_tien': tong_tien_tat_ca,
                'so_nguoi_dong_bhxh': so_nguoi_dong_bhxh,
                'redirect_url': redirect_url
            })
        except ValueError as e:
            return JsonResponse({'error': 'Định dạng ngày không hợp lệ'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Phương thức yêu cầu không hợp lệ'}, status=400)

@login_required
def redirect_bhxh_view(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    if nhanvien.vi_tri_cong_viec in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Kế toán']:
        return redirect('bhxh_list')
    else:
        return redirect('info_bhxh',ma_nv=nhanvien.id)
@login_required
def bhxh_cua_toi(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    bhxh_list = None
    if nhanvien.vi_tri_cong_viec in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Kế toán']:
        bhxh_list = BHXH.objects.filter(nhan_vien=nhanvien)
    return render(request, 'BHXH/BHXH.html', {'bhxh_list': bhxh_list, 'nhan_vien': nhanvien})


