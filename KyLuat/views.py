from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from HOME.models import KyLuat, KhenThuong, NhanVien
from .forms import KyLuatForm
from django.core.exceptions import PermissionDenied
from datetime import date
import logging

logger = logging.getLogger(__name__)

@login_required
def ky_luat_khen_thuong(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    # Lấy danh sách kỷ luật của chính người dùng
    ky_luat_cua_toi = KyLuat.objects.filter(nhan_vien=nhan_vien).order_by('-ngay_ra_quyet_dinh')
    thang_list_ky_luat = KyLuat.objects.filter(nhan_vien=nhan_vien).dates('ngay_bat_dau', 'month', order='DESC')
    nam_list_ky_luat = KyLuat.objects.filter(nhan_vien=nhan_vien).dates('ngay_bat_dau', 'year', order='DESC')

    # Lọc kỷ luật của chính người dùng theo tháng/năm
    thang = request.GET.get('thang')
    nam = request.GET.get('nam')
    if thang:
        ky_luat_cua_toi = ky_luat_cua_toi.filter(ngay_bat_dau__month=int(thang))
    if nam:
        ky_luat_cua_toi = ky_luat_cua_toi.filter(ngay_bat_dau__year=int(nam))

    # Lấy danh sách kỷ luật của nhân viên (nếu có quyền)
    ky_luat_list = KyLuat.objects.none()
    nhan_vien_list = NhanVien.objects.none()
    if request.user.has_perm('HOME.View_danh_sach_ky_luat'):
        if request.user.has_perm('HOME.view_all_ky_luat'):
            ky_luat_list = KyLuat.objects.all().order_by('-ngay_ra_quyet_dinh')
            nhan_vien_list = NhanVien.objects.all()
        else:
            ky_luat_list = KyLuat.objects.filter(nhan_vien__to_phong_ban=nhan_vien.to_phong_ban).order_by('-ngay_ra_quyet_dinh')
            nhan_vien_list = NhanVien.objects.filter(to_phong_ban=nhan_vien.to_phong_ban)

        # Lọc kỷ luật của nhân viên theo nhân viên/tháng/năm
        nhan_vien_id = request.GET.get('nhan_vien')
        if nhan_vien_id:
            ky_luat_list = ky_luat_list.filter(nhan_vien_id=nhan_vien_id)
        if thang:
            ky_luat_list = ky_luat_list.filter(ngay_bat_dau__month=int(thang))
        if nam:
            ky_luat_list = ky_luat_list.filter(ngay_bat_dau__year=int(nam))

    # Lấy danh sách khen thưởng của chính người dùng
    khen_thuong_list = KhenThuong.objects.filter(nhan_vien=nhan_vien).order_by('-ngay_tao')
    thang_list_khen_thuong = KhenThuong.objects.filter(nhan_vien=nhan_vien).dates('ngay_tao', 'month', order='DESC')
    nam_list_khen_thuong = KhenThuong.objects.filter(nhan_vien=nhan_vien).dates('ngay_tao', 'year', order='DESC')

    # Lọc khen thưởng của chính người dùng theo tháng/năm
    if thang:
        khen_thuong_list = khen_thuong_list.filter(ngay_tao__month=int(thang))
    if nam:
        khen_thuong_list = khen_thuong_list.filter(ngay_tao__year=int(nam))

    # Lấy danh sách khen thưởng của nhân viên (nếu có quyền)
    rewards = KhenThuong.objects.none()
    if request.user.has_perm('HOME.View_danh_sach_khen_thuong'):
        if request.user.has_perm('HOME.view_all_khenthuong'):
            rewards = KhenThuong.objects.all().order_by('-ngay_tao')
        else:
            rewards = KhenThuong.objects.filter(nhan_vien__to_phong_ban=nhan_vien.to_phong_ban).order_by('-ngay_tao')

        # Lọc khen thưởng của nhân viên theo nhân viên/tháng/năm
        if nhan_vien_id:
            rewards = rewards.filter(nhan_vien_id=nhan_vien_id)
        if thang:
            rewards = rewards.filter(ngay_tao__month=int(thang))
        if nam:
            rewards = rewards.filter(ngay_tao__year=int(nam))

    # Tạo danh sách tháng và năm mặc định
    from datetime import datetime
    default_thang_list = list(range(1, 13))
    current_year = datetime.now().year
    default_nam_list = list(range(2020, current_year + 2))

    # Gộp danh sách tháng và năm từ dữ liệu với danh sách mặc định
    thang_list_from_data = sorted(set([date.month for date in thang_list_ky_luat] + [date.month for date in thang_list_khen_thuong]), reverse=True) if thang_list_ky_luat or thang_list_khen_thuong else []
    nam_list_from_data = sorted(set([date.year for date in nam_list_ky_luat] + [date.year for date in nam_list_khen_thuong]), reverse=True) if nam_list_ky_luat or nam_list_khen_thuong else []

    thang_list = default_thang_list if not thang_list_from_data else sorted(set(default_thang_list + thang_list_from_data), reverse=True)
    nam_list = default_nam_list if not nam_list_from_data else sorted(set(default_nam_list + nam_list_from_data), reverse=True)

    context = {
        'ky_luat_cua_toi': ky_luat_cua_toi,
        'ky_luat_list': ky_luat_list,
        'khen_thuong_list': khen_thuong_list,
        'rewards': rewards,
        'nhan_vien_list': nhan_vien_list,
        'thang_list': thang_list,
        'nam_list': nam_list,
        'nhan_vien': nhan_vien,
        'has_permission': request.user.has_perm('HOME.View_danh_sach_ky_luat') or request.user.has_perm('HOME.View_danh_sach_khen_thuong'),
    }
    return render(request, 'KyLuat/ky_luat_khen_thuong.html', context)

@login_required
@permission_required('HOME.add_kyluat')
def add_ky_luat(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        logger.info(f"User {request.user.username} đang tạo kỷ luật")
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

                # Nếu người tạo có quyền toàn cục, tự động duyệt đơn
                if request.user.has_perm('HOME.add_kyluat_all'):
                    ky_luat.trang_thai = 'DA_DUYET'
                    ky_luat.nguoi_duyet_don = nhan_vien
                else:
                    ky_luat.trang_thai = 'DANG_CHO_DUYET'

                # Kiểm tra quyền dựa trên vị trí công việc
                if not request.user.has_perm('HOME.add_kyluat_all') and ky_luat.nhan_vien.vi_tri_cong_viec not in ['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh', 'Bếp', 'Y tế']:
                    raise PermissionDenied("Bạn chỉ có quyền tạo kỷ luật cho nhân viên có vị trí Giáo viên, Kế toán, Nhân sự, Tuyển sinh, Bếp, hoặc Y tế.")

                ky_luat.save()
                logger.info(f"Kỷ luật mới được tạo: ID={ky_luat.id}, Nhân viên={ky_luat.nhan_vien.ten_nv}, Trạng thái={ky_luat.trang_thai}")
                return redirect('ky_luat_khen_thuong')
            except Exception as e:
                logger.error(f"Lỗi khi lưu kỷ luật: {str(e)}", exc_info=True)
                form.add_error(None, f"Lỗi hệ thống khi lưu kỷ luật: {str(e)}. Vui lòng thử lại.")
        else:
            logger.warning(f"Form không hợp lệ: {form.errors.as_json()}")
    else:
        form = KyLuatForm(request=request)

    return render(request, 'KyLuat/Kyluat.html', {'form': form, 'form_errors': form.errors, 'nhan_vien': nhan_vien})

@login_required
@permission_required('HOME.change_kyluat')
def edit_ky_luat(request, ky_luat_id):
    ky_luat = get_object_or_404(KyLuat, id=ky_luat_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien != ky_luat.nguoi_tao_don and not request.user.has_perm('HOME.change_kyluat_all'):
            raise PermissionDenied("Bạn không có quyền chỉnh sửa đơn này.")
        if not request.user.has_perm('HOME.change_kyluat_all') and ky_luat.nhan_vien.vi_tri_cong_viec not in ['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh', 'Bếp', 'Y tế']:
            raise PermissionDenied("Bạn chỉ có quyền chỉnh sửa kỷ luật cho nhân viên có vị trí Giáo viên, Kế toán, Nhân sự, Tuyển sinh, Bếp, hoặc Y tế.")
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
                return redirect('ky_luat_khen_thuong')
            except Exception as e:
                logger.error(f"Lỗi khi chỉnh sửa kỷ luật: {str(e)}", exc_info=True)
                form.add_error(None, f"Lỗi hệ thống khi chỉnh sửa kỷ luật: {str(e)}. Vui lòng thử lại.")
    else:
        form = KyLuatForm(instance=ky_luat, request=request)
    return render(request, 'KyLuat/Kyluat.html', {'form': form, 'is_edit': True, 'form_errors': form.errors, 'nhan_vien': nhan_vien})

@login_required
@permission_required('HOME.View_duyet_ky_luat')
def duyet_ky_luat(request, ky_luat_id):
    ky_luat = get_object_or_404(KyLuat, id=ky_luat_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if ky_luat.nguoi_duyet_don != nhan_vien:
            logger.warning(f"User {request.user.username} không phải người được chỉ định duyệt đơn ID={ky_luat.id}")
            raise PermissionDenied("Bạn không phải người được chỉ định để duyệt đơn này.")
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            if action == 'approve':
                ky_luat.trang_thai = 'DA_DUYET'
                ky_luat.nguoi_duyet_don = nhan_vien
                if not ky_luat.ngay_ra_quyet_dinh:
                    ky_luat.ngay_ra_quyet_dinh = date.today()
                ky_luat.save()
                logger.info(f"Đơn kỷ luật ID={ky_luat.id} đã được duyệt bởi {nhan_vien.ten_nv}")
            elif action == 'reject':
                ky_luat.trang_thai = 'DA_TU_CHOI'
                ky_luat.nguoi_duyet_don = nhan_vien
                ky_luat.save()
                logger.info(f"Đơn kỷ luật ID={ky_luat.id} đã bị từ chối bởi {nhan_vien.ten_nv}")
            return redirect('ky_luat_cho_duyet')
        except Exception as e:
            logger.error(f"Lỗi khi xử lý đơn kỷ luật ID={ky_luat.id}: {str(e)}", exc_info=True)
            return render(request, 'KyLuat/Duyet_kyluat.html', {
                'ky_luat': ky_luat,
                'error': f"Lỗi hệ thống khi xử lý đơn: {str(e)}. Vui lòng thử lại."
            })
    return render(request, 'KyLuat/Duyet_kyluat.html', {'ky_luat': ky_luat, 'nhan_vien': nhan_vien})

@login_required
@permission_required('HOME.View_duyet_ky_luat')
def ky_luat_cho_duyet(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.user.has_perm('HOME.view_all_ky_luat'):
        ky_luat_list = KyLuat.objects.filter(trang_thai='DANG_CHO_DUYET').order_by('-ngay_ra_quyet_dinh')
    else:
        ky_luat_list = KyLuat.objects.filter(trang_thai='DANG_CHO_DUYET', nguoi_duyet_don=nhan_vien).order_by('-ngay_ra_quyet_dinh')

    return render(request, 'KyLuat/Kyluat_cho_duyet.html', {
        'ky_luat_list': ky_luat_list, 'nhan_vien': nhan_vien,
    })

@login_required
@permission_required('HOME.View_danh_sach_ky_luat')
def ky_luat_list(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.user.has_perm('HOME.view_all_ky_luat'):
        ky_luat_list = KyLuat.objects.all().order_by('-ngay_ra_quyet_dinh')
        nhan_vien_list = NhanVien.objects.all()
    else:
        ky_luat_list = KyLuat.objects.filter(nhan_vien__to_phong_ban=nhan_vien.to_phong_ban).order_by('-ngay_ra_quyet_dinh')
        nhan_vien_list = NhanVien.objects.filter(to_phong_ban=nhan_vien.to_phong_ban)

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
    })

@login_required
@permission_required('HOME.delete_kyluat')
def xoa_ky_luat(request, ky_luat_id, **kwargs):
    ky_luat = get_object_or_404(KyLuat, id=ky_luat_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien != ky_luat.nguoi_tao_don and not request.user.has_perm('HOME.delete_kyluat_all'):
            raise PermissionDenied("Bạn không có quyền xóa đơn này.")
        if not request.user.has_perm('HOME.delete_kyluat_all') and ky_luat.nhan_vien.vi_tri_cong_viec not in ['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh', 'Bếp', 'Y tế']:
            raise PermissionDenied("Bạn chỉ có quyền xóa kỷ luật cho nhân viên có vị trí Giáo viên, Kế toán, Nhân sự, Tuyển sinh, Bếp, hoặc Y tế.")
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")
    ky_luat.delete()
    return redirect('ky_luat_khen_thuong')

@login_required
def ky_luat_cua_toi(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    ky_luat_list = KyLuat.objects.filter(nhan_vien=nhan_vien).order_by('-ngay_ra_quyet_dinh')
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
    })