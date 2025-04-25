from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from HOME.models import KyLuat, NhanVien
from .forms import KyLuatForm
from django.core.exceptions import PermissionDenied
from datetime import date
import logging

logger = logging.getLogger(__name__)

@login_required
def add_ky_luat(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        logger.info(f"User {request.user.username} (chuc_vu: {nhan_vien.chuc_vu}) đang tạo kỷ luật")
        if nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng']:
            logger.warning(f"User {request.user.username} không có quyền tạo đơn")
            raise PermissionDenied("Bạn không có quyền tạo đơn kỷ luật.")
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        form = KyLuatForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            try:
                ky_luat = form.save(commit=False)
                if not ky_luat.ngay_ra_quyet_dinh:
                    ky_luat.ngay_ra_quyet_dinh = date.today()
                ky_luat.trang_thai = 'DANG_CHO_DUYET'
                ky_luat.save()
                logger.info(f"Kỷ luật mới được tạo: ID={ky_luat.id}, Nhân viên={ky_luat.nhan_vien.ten_nv}")
                return redirect('ky_luat_list')
            except Exception as e:
                logger.error(f"Lỗi khi lưu kỷ luật: {str(e)}", exc_info=True)
                form.add_error(None, f"Lỗi hệ thống khi lưu kỷ luật: {str(e)}. Vui lòng thử lại.")
        else:
            logger.warning(f"Form không hợp lệ: {form.errors.as_json()}")
    else:
        form = KyLuatForm(request=request)

    return render(request, 'KyLuat/Kyluat.html', {'form': form, 'form_errors': form.errors})

@login_required
def edit_ky_luat(request, ky_luat_id):
    ky_luat = get_object_or_404(KyLuat, id=ky_luat_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien != ky_luat.nguoi_tao_don and nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']:
            raise PermissionDenied("Bạn không có quyền chỉnh sửa đơn này.")
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        form = KyLuatForm(request.POST, request.FILES, instance=ky_luat, request=request)
        if form.is_valid():
            try:
                ky_luat = form.save(commit=False)
                ky_luat.trang_thai = ky_luat.trang_thai or 'DANG_CHO_DUYET'
                if request.POST.get('xoa_minh_chung_file') and ky_luat.minh_chung_file:
                    ky_luat.minh_chung_file.delete()
                    ky_luat.minh_chung_file = None
                if request.POST.get('xoa_minh_chung_url'):
                    ky_luat.minh_chung_url = None
                ky_luat.save()
                logger.info(f"Kỷ luật được chỉnh sửa: ID={ky_luat.id}, Nhân viên={ky_luat.nhan_vien.ten_nv}")
                return redirect('ky_luat_list')
            except Exception as e:
                logger.error(f"Lỗi khi chỉnh sửa kỷ luật: {str(e)}", exc_info=True)
                form.add_error(None, f"Lỗi hệ thống khi chỉnh sửa kỷ luật: {str(e)}. Vui lòng thử lại.")
    else:
        form = KyLuatForm(instance=ky_luat, request=request)
    return render(request, 'KyLuat/Kyluat.html', {'form': form, 'is_edit': True, 'form_errors': form.errors})

@login_required
def duyet_ky_luat(request, ky_luat_id):
    ky_luat = get_object_or_404(KyLuat, id=ky_luat_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien.chuc_vu != 'Hiệu Trưởng':
            raise PermissionDenied("Chỉ T có quyền duyệt đơn này.")
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        ky_luat.trang_thai = 'DA_DUYET'
        ky_luat.nguoi_duyet_don = nhan_vien
        if not ky_luat.ngay_ra_quyet_dinh:
            ky_luat.ngay_ra_quyet_dinh = date.today()
        ky_luat.save()
        return redirect('ky_luat_cho_duyet')
    return render(request, 'KyLuat/Duyet_kyluat.html', {'ky_luat': ky_luat})

@login_required
def ky_luat_cho_duyet(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']:
            raise PermissionDenied("Bạn không có quyền xem danh sách đơn chờ duyệt.")
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    ky_luat_list = KyLuat.objects.filter(trang_thai='DANG_CHO_DUYET', nguoi_duyet_don=nhan_vien)
    return render(request, 'KyLuat/Kyluat_cho_duyet.html', {
        'ky_luat_list': ky_luat_list,
    })

@login_required
def ky_luat_list(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng']:
            return redirect('ky_luat_cua_toi')  # Chuyển hướng đến Kỷ luật của tôi
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if nhan_vien.chuc_vu == 'Tổ trưởng':
        # Tổ trưởng chỉ thấy kỷ luật của nhân viên trong tổ
        ky_luat_list = KyLuat.objects.filter(nhan_vien__to_phong_ban=nhan_vien.to_phong_ban)
        nhan_vien_list = NhanVien.objects.filter(to_phong_ban=nhan_vien.to_phong_ban)
    else:
        # Hiệu trưởng/Hiệu phó thấy tất cả kỷ luật
        ky_luat_list = KyLuat.objects.all()
        nhan_vien_list = NhanVien.objects.all()

    thang_list = KyLuat.objects.dates('ngay_bat_dau', 'month', order='DESC')
    nam_list = KyLuat.objects.dates('ngay_bat_dau', 'year', order='DESC')

    nhan_vien_id = request.GET.get('nhan_vien')
    thang = request.GET.get('thang')
    nam = request.GET.get('nam')

    if nhan_vien_id:
        ky_luat_list = ky_luat_list.filter(nhan_vien_id=nhan_vien_id)
    if thang:
        ky_luat_list = ky_luat_list.filter(ngay_bat_dau__month=int(thang))
    if nam:
        ky_luat_list = ky_luat_list.filter(ngay_bat_dau__year=int(nam))

    return render(request, 'KyLuat/Kyluat_list.html', {
        'ky_luat_list': ky_luat_list,
        'nhan_vien_list': nhan_vien_list,
        'thang_list': [date.month for date in thang_list],
        'nam_list': [date.year for date in nam_list],
        'user_nhan_vien': nhan_vien,
        'allowed_roles': ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng'],  # Thêm danh sách chức vụ
    })

@login_required
def xoa_ky_luat(request, ky_luat_id, **kwargs):
    ky_luat = get_object_or_404(KyLuat, id=ky_luat_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien != ky_luat.nguoi_tao_don and nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động']:
            raise PermissionDenied("Bạn không có quyền xóa đơn này.")
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")
    ky_luat.delete()
    return redirect('ky_luat_list')

@login_required
def ky_luat_cua_toi(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    ky_luat_list = KyLuat.objects.filter(nhan_vien=nhan_vien)
    thang_list = KyLuat.objects.filter(nhan_vien=nhan_vien).dates('ngay_bat_dau', 'month', order='DESC')
    nam_list = KyLuat.objects.filter(nhan_vien=nhan_vien).dates('ngay_bat_dau', 'year', order='DESC')
    thang = request.GET.get('thang')
    nam = request.GET.get('nam')

    if thang:
        ky_luat_list = ky_luat_list.filter(ngay_bat_dau__month=int(thang))
    if nam:
        ky_luat_list = ky_luat_list.filter(ngay_bat_dau__year=int(nam))

    tieu_de = f"Kỷ luật của {nhan_vien.ten_nv}"
    return render(request, 'KyLuat/KLNV.html', {
        'ky_luat_list': ky_luat_list,
        'tieu_de': tieu_de,
        'thang_list': [date.month for date in thang_list],
        'nam_list': [date.year for date in nam_list],
        'user_nhan_vien': nhan_vien,
        'allowed_roles': ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng'],  # Thêm danh sách chức vụ
    })

@login_required
def ky_luat_nhan_vien(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien.chuc_vu not in ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng']:
            return redirect('ky_luat_cua_toi')  # Chuyển hướng đến Kỷ luật của tôi
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if nhan_vien.chuc_vu == 'Tổ trưởng':
        ky_luat_list = KyLuat.objects.filter(nhan_vien__to_phong_ban=nhan_vien.to_phong_ban)
        nhan_vien_list = NhanVien.objects.filter(to_phong_ban=nhan_vien.to_phong_ban).exclude(id=nhan_vien.id)
    else:
        ky_luat_list = KyLuat.objects.all()
        nhan_vien_list = NhanVien.objects.all().exclude(id=nhan_vien.id)

    thang_list = KyLuat.objects.dates('ngay_bat_dau', 'month', order='DESC')
    nam_list = KyLuat.objects.dates('ngay_bat_dau', 'year', order='DESC')

    nhan_vien_id = request.GET.get('nhan_vien')
    thang = request.GET.get('thang')
    nam = request.GET.get('nam')

    if nhan_vien_id:
        ky_luat_list = ky_luat_list.filter(nhan_vien_id=nhan_vien_id)
    if thang:
        ky_luat_list = ky_luat_list.filter(ngay_bat_dau__month=int(thang))
    if nam:
        ky_luat_list = ky_luat_list.filter(ngay_bat_dau__year=int(nam))

    tieu_de = "Kỷ luật của nhân viên"
    return render(request, 'KyLuat/Kyluat_nhan_vien.html', {
        'ky_luat_list': ky_luat_list,
        'nhan_vien_list': nhan_vien_list,
        'thang_list': [date.month for date in thang_list],
        'nam_list': [date.year for date in nam_list],
        'tieu_de': tieu_de,
        'user_nhan_vien': nhan_vien,
        'allowed_roles': ['Hiệu Trưởng', 'Hiệu phó chuyên môn', 'Hiệu phó hoạt động', 'Tổ trưởng'],  # Thêm danh sách chức vụ
    })