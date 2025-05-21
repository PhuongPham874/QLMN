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
    bhxh_list = BHXH.objects.all().order_by('nhan_vien__id')
    # mới
    # Lọc theo id nhân viên từ GET parameter
    nv_id = request.GET.get('nv_id')
    if nv_id:
        bhxh_list = bhxh_list.filter(nhan_vien__id=nv_id)
    #  Lấy danh sách nhân viên có BHXH
    ds_nhanvien = NhanVien.objects.filter(id__in=bhxh_list.values_list('nhan_vien__id', flat=True))

    form = DongBHXHForm()
    return render(request, 'BHXH/BHXH.html', {
        'bhxh_list': bhxh_list,
        'nhan_vien': nhanvien,
        'ds_nhanvien': ds_nhanvien,  #  Chỉ những nhân viên có BHXH
        'form': form,
        'selected_nv_id': nv_id if nv_id else '',
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
                loai_hop_dong='Hợp đồng có thời hạn'
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
            messages.error(request, "Vui lòng kiểm tra lại thông tin.")
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
# mới
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import datetime
# @csrf_exempt
# def tinh_tien_bhxh_ajax(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Phương thức không hợp lệ"}, status=400)
#
#     try:
#         start = request.POST.get("ngay_bat_dau")
#         end = request.POST.get("ngay_ket_thuc")
#         start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
#         end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
#
#         if start_date >= end_date:
#             return JsonResponse({"error": "Ngày bắt đầu phải nhỏ hơn ngày kết thúc"}, status=400)
#
#         # Kiểm tra khoảng thời gian trùng
#         if DONGBHXH.objects.filter(
#             ngay_bat_dau__lte=end_date,
#             ngay_ket_thuc__gte=start_date,
#         ).exists():
#             return JsonResponse({"error": "Khoảng thời gian đã tồn tại"}, status=400)
#
#         bhxh_list = BHXH.objects.select_related("nhan_vien")
#         tong_tien = 0
#         so_nguoi = bhxh_list.count()
#
#         # Tính tổng tiền tất cả nhân viên
#         for bhxh in bhxh_list:
#             nhan_vien = bhxh.nhan_vien
#             tong_tien += int(tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong))
#
#         # Nếu submit thì lưu từng bản ghi riêng cho từng người
#         if "submit" in request.POST:
#             for bhxh in bhxh_list:
#                 nhan_vien = bhxh.nhan_vien
#                 tien_bhxh = int(tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong))
#                 DONGBHXH.objects.create(
#                     nhan_vien=nhan_vien,
#                     ngay_bat_dau=start_date,
#                     ngay_ket_thuc=end_date,
#                     tong_tien=tien_bhxh,
#                 )
#             return JsonResponse({
#                 "message": f"Đã nộp BHXH cho {so_nguoi} người, tổng tiền {tong_tien:,} VNĐ",
#                 "tong_tien": tong_tien,
#                 "redirect_url": reverse("bhxh_list"),
#             })
#
#         # Trả về tổng tiền và số người nếu chưa submit
#         return JsonResponse({
#             "tong_tien": tong_tien,
#             'so_nguoi_dong': so_nguoi,
#             "redirect_url": reverse("bhxh_list"),
#         })
#
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=400)
@csrf_exempt
def tinh_tien_bhxh_ajax(request):
    if request.method == "POST":
        start = request.POST.get("ngay_bat_dau")
        end = request.POST.get("ngay_ket_thuc")
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        if start_date >= end_date:
            return JsonResponse({"error": "Ngày bắt đầu phải nhỏ hơn ngày kết thúc"}, status=400)
        # Kiểm tra khoảng thời gian trùng
        if DONGBHXH.objects.filter(
            ngay_bat_dau__lte=end_date,
            ngay_ket_thuc__gte=start_date,
        ).exists():
            return JsonResponse({"error": "Khoảng thời gian đã tồn tại"}, status=400)

        bhxh_list = BHXH.objects.select_related("nhan_vien")
        tong_tien = 0
        so_nguoi = bhxh_list.count()

        # Tính tổng tiền tất cả nhân viên
        for bhxh in bhxh_list:
            nhan_vien = bhxh.nhan_vien
            tong_tien += int(tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong))

        # Nếu submit thì lưu từng bản ghi riêng cho từng người
        if "submit" in request.POST:
            for bhxh in bhxh_list:
                nhan_vien = bhxh.nhan_vien
                tien_bhxh = int(tinh_tong_tien_bhxh(nhan_vien, bhxh.nhan_vien_dong, bhxh.truong_dong))
                DONGBHXH.objects.create(
                    nhan_vien=nhan_vien,
                    ngay_bat_dau=start_date,
                    ngay_ket_thuc=end_date,
                    tong_tien=tien_bhxh,
                )

            # Thêm thông báo vào session
            messages.success(
                request,
                f" Đã nộp BHXH cho {so_nguoi} người, tổng tiền {tong_tien:,} VNĐ"
            )

            return JsonResponse({
                "redirect_url": reverse("bhxh_list"),
            })

        # Trả về tổng tiền và số người nếu chưa submit
        return JsonResponse({
            "tong_tien": tong_tien,
            'so_nguoi_dong': so_nguoi,
            "redirect_url": reverse("bhxh_list"),
        })
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


