from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from HOME.models import KhenThuong, NhanVien
from .forms import KhenThuongForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('HOME.add_khenthuong')
def add_khen_thuong(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        form = KhenThuongForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                khen_thuong = form.save(commit=False)
                khen_thuong.nguoi_tao_don = nhan_vien
                # Kiểm tra quyền dựa trên vị trí công việc
                if not request.user.has_perm('HOME.add_khenthuong_all') and khen_thuong.nhan_vien.vi_tri_cong_viec not in ['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh', 'Bếp', 'Y tế']:
                    raise PermissionDenied("Bạn chỉ có quyền tạo khen thưởng cho nhân viên có vị trí Giáo viên, Kế toán, Nhân sự, Tuyển sinh, Bếp, hoặc Y tế.")
                khen_thuong.save()
                logger.info(f"Khen thưởng mới được tạo: ID={khen_thuong.id}, Nhân viên={khen_thuong.nhan_vien.ten_nv}, Trạng thái={khen_thuong.trang_thai}")
                return redirect('ky_luat_khen_thuong')
            except Exception as e:
                logger.error(f"Lỗi khi lưu khen thưởng: {str(e)}", exc_info=True)
                form.add_error(None, f"Lỗi hệ thống khi lưu khen thưởng: {str(e)}. Vui lòng thử lại.")
        else:
            logger.warning(f"Form không hợp lệ: {form.errors.as_json()}")
    else:
        form = KhenThuongForm(initial={'nguoi_tao_don': nhan_vien}, user=request.user)

    return render(request, 'KhenThuong/Khenthuong.html', {'form': form, 'form_errors': form.errors, 'nhan_vien': nhan_vien})

@login_required
@permission_required('HOME.change_khenthuong')
def edit_khen_thuong(request, reward_id):
    khen_thuong = get_object_or_404(KhenThuong, id=reward_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien != khen_thuong.nguoi_tao_don and not request.user.has_perm('HOME.change_khenthuong_all'):
            logger.warning(f"User {request.user.username} không có quyền chỉnh sửa đơn")
            raise PermissionDenied("Bạn không có quyền chỉnh sửa đơn này.")
        if not request.user.has_perm('HOME.change_khenthuong_all') and khen_thuong.nhan_vien.vi_tri_cong_viec not in ['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh', 'Bếp', 'Y tế']:
            raise PermissionDenied("Bạn chỉ có quyền chỉnh sửa khen thưởng cho nhân viên có vị trí Giáo viên, Kế toán, Nhân sự, Tuyển sinh, Bếp, hoặc Y tế.")
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        form = KhenThuongForm(request.POST, request.FILES, instance=khen_thuong, user=request.user)
        if form.is_valid():
            try:
                khen_thuong = form.save(commit=False)
                if request.POST.get('xoa_minh_chung_file') and khen_thuong.minh_chung_file:
                    khen_thuong.minh_chung_file.delete()
                    khen_thuong.minh_chung_file = None
                if request.POST.get('xoa_minh_chung_url'):
                    khen_thuong.minh_chung_url = None
                khen_thuong.save()
                logger.info(f"Khen thưởng được chỉnh sửa: ID={khen_thuong.id}, Nhân viên={khen_thuong.nhan_vien.ten_nv}")
                return redirect('ky_luat_khen_thuong')
            except Exception as e:
                logger.error(f"Lỗi khi chỉnh sửa khen thưởng: {str(e)}", exc_info=True)
                form.add_error(None, f"Lỗi hệ thống khi chỉnh sửa khen thưởng: {str(e)}. Vui lòng thử lại.")
    else:
        form = KhenThuongForm(instance=khen_thuong, user=request.user)

    return render(request, 'KhenThuong/Khenthuong.html', {'form': form, 'is_edit': True, 'form_errors': form.errors, 'nhan_vien': nhan_vien})

@login_required
@permission_required('HOME.View_duyet_khen_thuong')
def duyet_khen_thuong(request, reward_id):
    khen_thuong = get_object_or_404(KhenThuong, id=reward_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if khen_thuong.nguoi_xac_nhan and nhan_vien != khen_thuong.nguoi_xac_nhan:
            logger.warning(f"User {request.user.username} không phải người được chỉ định duyệt đơn")
            raise PermissionDenied("Bạn không phải người được chỉ định để duyệt đơn này.")
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            if action == 'approve':
                khen_thuong.trang_thai = 'DA_DUYET'
                khen_thuong.nguoi_xac_nhan = nhan_vien
                khen_thuong.save()
                logger.info(f"Khen thưởng được duyệt: ID={khen_thuong.id}, Nhân viên={khen_thuong.nhan_vien.ten_nv}")
            elif action == 'reject':
                khen_thuong.trang_thai = 'DA_TU_CHOI'
                khen_thuong.nguoi_xac_nhan = nhan_vien
                khen_thuong.save()
                logger.info(f"Khen thưởng bị từ chối: ID={khen_thuong.id}, Nhân viên={khen_thuong.nhan_vien.ten_nv}")
            return redirect('khen_thuong_cho_duyet')
        except Exception as e:
            logger.error(f"Lỗi khi xử lý khen thưởng: {str(e)}", exc_info=True)
            return render(request, 'KhenThuong/Duyet_khenthuong.html', {
                'khen_thuong': khen_thuong,
                'error': f"Lỗi hệ thống khi xử lý đơn: {str(e)}. Vui lòng thử lại."
            })

    return render(request, 'KhenThuong/Duyet_khenthuong.html', {'khen_thuong': khen_thuong, 'nhan_vien': nhan_vien})

@login_required
@permission_required('HOME.View_duyet_khen_thuong')
def khen_thuong_cho_duyet(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    if request.user.has_perm('HOME.view_all_khenthuong'):
        rewards = KhenThuong.objects.filter(trang_thai='DANG_CHO_DUYET').order_by('-ngay_tao')
    else:
        rewards = KhenThuong.objects.filter(trang_thai='DANG_CHO_DUYET', nguoi_xac_nhan=nhan_vien).order_by('-ngay_tao')

    thang_list = rewards.dates('ngay_tao', 'month', order='DESC')
    nam_list = rewards.dates('ngay_tao', 'year', order='DESC')

    thang = request.GET.get('thang')
    nam = request.GET.get('nam')

    if thang:
        rewards = rewards.filter(ngay_tao__month=int(thang))
    if nam:
        rewards = rewards.filter(ngay_tao__year=int(nam))

    context = {
        'rewards': rewards,
        'thang_list': [date.month for date in thang_list],
        'nam_list': [date.year for date in nam_list],
        'nhan_vien': nhan_vien,
        'can_approve': request.user.has_perm('HOME.View_duyet_khen_thuong'),
    }
    return render(request, 'KhenThuong/Khenthuong_cho_duyet.html', context)

@login_required
@permission_required('HOME.View_danh_sach_khen_thuong')
def khen_thuong_list(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    rewards = KhenThuong.objects.none()
    nhan_vien_list = NhanVien.objects.none()
    error_message = None

    # Debug: Kiểm tra thông tin user và nhóm
    print(f"khen_thuong_list - User: {request.user.username}, Groups: {[g.name for g in request.user.groups.all()]}, vi_tri_cong_viec: {nhan_vien.vi_tri_cong_viec}")

    if request.user.groups.filter(name='HieuTruong').exists():
        rewards = KhenThuong.objects.all().order_by('-ngay_tao')
        nhan_vien_list = NhanVien.objects.all().exclude(id=nhan_vien.id)
    elif request.user.groups.filter(name='ToTruong').exists():
        rewards = KhenThuong.objects.filter(nhan_vien__to_phong_ban=nhan_vien.to_phong_ban).order_by('-ngay_tao')
        nhan_vien_list = NhanVien.objects.filter(to_phong_ban=nhan_vien.to_phong_ban).exclude(id=nhan_vien.id)
        if not rewards.exists():
            error_message = "Không có khen thưởng nào trong tổ/phòng ban của bạn."
    elif request.user.groups.filter(name='HieuPho').exists():
        if nhan_vien.vi_tri_cong_viec == 'Hiệu phó chuyên môn':
            rewards = KhenThuong.objects.filter(nhan_vien__vi_tri_cong_viec__in=['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh']).order_by('-ngay_tao')
            nhan_vien_list = NhanVien.objects.filter(vi_tri_cong_viec__in=['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh']).exclude(id=nhan_vien.id)
            if not rewards.exists():
                error_message = "Không có khen thưởng nào cho các vị trí Giáo viên, Kế toán, Nhân sự, hoặc Tuyển sinh."
        elif nhan_vien.vi_tri_cong_viec == 'Hiệu phó hoạt động':
            rewards = KhenThuong.objects.filter(nhan_vien__vi_tri_cong_viec__in=['Bếp', 'Y - tế']).order_by('-ngay_tao')
            nhan_vien_list = NhanVien.objects.filter(vi_tri_cong_viec__in=['Bếp', 'Y - tế']).exclude(id=nhan_vien.id)
            if not rewards.exists():
                error_message = "Không có khen thưởng nào cho các vị trí Bếp hoặc Y - tế."
        else:
            error_message = f"Vị trí công việc '{nhan_vien.vi_tri_cong_viec}' không được hỗ trợ để xem danh sách khen thưởng."

    # Debug: Kiểm tra số lượng khen thưởng và nhân viên
    print(f"khen_thuong_list - rewards count: {rewards.count()}, nhan_vien_list count: {nhan_vien_list.count()}")

    thang_list = KhenThuong.objects.dates('ngay_tao', 'month', order='DESC')
    nam_list = KhenThuong.objects.dates('ngay_tao', 'year', order='DESC')

    nhan_vien_id = request.GET.get('nhan_vien')
    thang = request.GET.get('thang')
    nam = request.GET.get('nam')

    if nhan_vien_id:
        rewards = rewards.filter(nhan_vien_id=int(nhan_vien_id))
    if thang:
        rewards = rewards.filter(ngay_tao__month=int(thang))
    if nam:
        rewards = rewards.filter(ngay_tao__year=int(nam))

    context = {
        'rewards': rewards,
        'nhan_vien_list': nhan_vien_list,
        'thang_list': [date.month for date in thang_list],
        'nam_list': [date.year for date in nam_list],
        'user_nhan_vien': nhan_vien,
        'allowed_roles': ['HieuTruong', 'HieuPho', 'ToTruong'],
        'error_message': error_message,
        # 'can_approve': request.user.has_perm('HOME.View_duyet_khen_thuong'),
    }
    return render(request, 'KhenThuong/Khenthuong_list.html', context)

@login_required
@permission_required('HOME.delete_khenthuong')
def xoa_khen_thuong(request, reward_id):
    khen_thuong = get_object_or_404(KhenThuong, id=reward_id)
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
        if nhan_vien != khen_thuong.nguoi_tao_don and not request.user.has_perm('HOME.delete_khenthuong_all'):
            logger.warning(f"User {request.user.username} không có quyền xóa đơn")
            raise PermissionDenied("Bạn không có quyền xóa đơn này.")
        if not request.user.has_perm('HOME.delete_khenthuong_all') and khen_thuong.nhan_vien.vi_tri_cong_viec not in ['Giáo viên', 'Kế toán', 'Nhân sự', 'Tuyển sinh', 'Bếp', 'Y tế']:
            raise PermissionDenied("Bạn chỉ có quyền xóa khen thưởng cho nhân viên có vị trí Giáo viên, Kế toán, Nhân sự, Tuyển sinh, Bếp, hoặc Y tế.")
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")
    khen_thuong.delete()
    logger.info(f"Khen thưởng đã bị xóa: ID={khen_thuong.id}")
    return redirect('ky_luat_khen_thuong')

@login_required
def khen_thuong_cua_toi(request):
    try:
        nhan_vien = NhanVien.objects.get(user=request.user)
    except NhanVien.DoesNotExist:
        logger.error(f"Không tìm thấy nhân viên cho user {request.user.username}")
        raise PermissionDenied("Bạn không phải nhân viên hợp lệ.")

    khen_thuong_list = KhenThuong.objects.filter(nhan_vien=nhan_vien).order_by('-ngay_tao')
    thang_list = KhenThuong.objects.filter(nhan_vien=nhan_vien).dates('ngay_tao', 'month', order='DESC')
    nam_list = KhenThuong.objects.filter(nhan_vien=nhan_vien).dates('ngay_tao', 'year', order='DESC')
    thang = request.GET.get('thang')
    nam = request.GET.get('nam')

    if thang:
        khen_thuong_list = khen_thuong_list.filter(ngay_tao__month=int(thang))
    if nam:
        khen_thuong_list = khen_thuong_list.filter(ngay_tao__year=int(nam))

    context = {
        'khen_thuong_list': khen_thuong_list,
        'tieu_de': f"Khen thưởng của {nhan_vien.ten_nv}",
        'thang_list': [date.month for date in thang_list],
        'nam_list': [date.year for date in nam_list],
        'nhan_vien': nhan_vien,
        'can_approve': request.user.has_perm('HOME.View_duyet_khen_thuong'),
    }
    return render(request, 'KhenThuong/KTNV.html', context)