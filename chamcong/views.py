from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from HOME.models import ChamCong, NhanVien
from collections import defaultdict

@login_required
def cham_cong(request):
    nhan_vien = NhanVien.objects.get(user=request.user)

    # Lấy tháng và năm từ query parameters
    selected_month = request.GET.get('month', str(timezone.now().month).zfill(2))
    selected_year = request.GET.get('year', str(timezone.now().year))

    # Lấy tất cả các bản ghi chấm công
    records = ChamCong.objects.filter(nhan_vien=nhan_vien).order_by('ngay')

    # Gom theo tháng/năm
    cham_cong_theo_thang = defaultdict(list)
    for record in records:
        key = record.ngay.strftime("%Y-%m")  # dạng: 2025-04
        cham_cong_theo_thang[key].append(record)


    cham_cong_theo_thang = dict(sorted(cham_cong_theo_thang.items(), reverse=True))


    months = ChamCong.objects.filter(nhan_vien=nhan_vien).values('ngay__month').distinct().order_by('ngay__month')
    years = ChamCong.objects.filter(nhan_vien=nhan_vien).values('ngay__year').distinct().order_by('ngay__year')

    return render(request, "ChamCong/cham_cong.html", {
        "nhan_vien": nhan_vien,
        "cham_cong_theo_thang": cham_cong_theo_thang,
        "months": months,
        "years": years,
        "selected_month": selected_month,
        "selected_year": selected_year,
    })