from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from HOME.models import NghiPhep, NhanVien, HopDongLaoDong, PhuCapNhanVien, PhuCap
from .forms import NghiPhepForm, SearchForm, Ghichu, loai_nghi_phep, SearchNVForm
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import datetime, date
from django.utils.timezone import now


def tinh_so_nghi_phep_nam(ngay_bat_dau_lam: date, nam: int, tong_so_ngay_phep_nam: int = 12):
    if ngay_bat_dau_lam.year > nam:
        return 0
    if ngay_bat_dau_lam.year < nam:
        return tong_so_ngay_phep_nam
    thang_bat_dau = ngay_bat_dau_lam.month
    so_thang_lam_viec = 12 - thang_bat_dau + 1
    return round((so_thang_lam_viec / 12) * tong_so_ngay_phep_nam)

def ThongTinNPYear(request, year):
    years = NghiPhep.objects.values_list('ngay_tao_don__year', flat=True).distinct().order_by('-ngay_tao_don__year')
    #year = request.GET.get('year')
    if year is None:
        year = now().year
    else:
        year = int(year)
    return {'year':year,
            'years': years}

def ThongTinNP( request,nhanvien, danh_sach, nam):
    thong_tin = ThongTinNPYear(request,nam)
    year = thong_tin['year']
    today = timezone.now().date()
    so_ngay_da_nghi = 0
    so_ngay_da_nghi_PN=0
    so_ngay = 0
    for don in danh_sach:
        if don.trang_thai_don =="Đã duyệt":
            so_ngay = (don.ngay_ket_thuc - don.ngay_bat_dau).days
            so_ngay_da_nghi += so_ngay


        # Nếu là loại nghỉ phép năm thì cộng thêm riêng
        if don.loai_nghi == 'Nghỉ phép năm' and don.trang_thai_don =="Đã duyệt":
            so_ngay_da_nghi_PN += so_ngay

    hop_dong = HopDongLaoDong.objects.get(nhan_vien=nhanvien)
    ngay_vao_lam = hop_dong.tu_ngay
    so_nghi_phep_nam = tinh_so_nghi_phep_nam(ngay_vao_lam, year)



    Pn_conlai = so_nghi_phep_nam - so_ngay_da_nghi_PN;
    so_don = danh_sach.count();
    so_don_dang_cho_duyet = NghiPhep.objects.filter(nhan_vien=nhanvien, trang_thai_don='Đang chờ duyệt',
                                                    ngay_tao_don__year=year)
    so_don_da_duyet = NghiPhep.objects.filter(nhan_vien=nhanvien, trang_thai_don='Đã duyệt', ngay_tao_don__year=year)
    so_don_dang_bi_tu_choi = NghiPhep.objects.filter(nhan_vien=nhanvien, trang_thai_don='Bị từ chối',
                                                     ngay_tao_don__year=year)
    return {
        'so_ngay_da_nghi': so_ngay_da_nghi,
        'PN_con_lai': Pn_conlai,
        'so_don': so_don,
        'so_nghi_phep_nam':so_nghi_phep_nam,
        'so_don_dang_duyet': so_don_dang_cho_duyet,
        'so_don_da_duyet': so_don_da_duyet,
        'so_don_dang_bi_tu_choi': so_don_dang_bi_tu_choi,
        **ThongTinNPYear(request, nam)
    }




@login_required
def NghiPhep_list_nv(request):
    nam = request.GET.get('year')
    thong_tin = ThongTinNPYear(request, nam)
    year = thong_tin['year']
    nhanvien = get_object_or_404(NhanVien, user = request.user)
    nghiphep_list_nv = NghiPhep.objects.filter(nhan_vien = nhanvien, ngay_tao_don__year=year).order_by('-ngay_tao_don')
    form = SearchForm(request.GET)

    ThongTinNP(request,nhanvien, nghiphep_list_nv, year)

    context = {
        'NP_list': nghiphep_list_nv,
        'nhan_vien': nhanvien,
        'form': form,
        **ThongTinNP(request, nhanvien, nghiphep_list_nv, year)
    }
    return render(request, 'NghiPhep/NP_list.html', context)

@login_required
def NP_nv_search(request):


    form = SearchForm(request.GET)
    search =""
    if form.is_valid(): #dap ung cac dk cua SearchForm
        search = form.cleaned_data.get("search","")#chuỗi
        search_date = form.cleaned_data['search']  # Đây là đối tượng date
        year = search_date.year
        nhanvien = get_object_or_404(NhanVien, user=request.user)
        nghiphep_all_nv = NghiPhep.objects.filter(nhan_vien=nhanvien,ngay_tao_don__year=year )
        danh_sach = nghiphep_all_nv.filter(ngay_bat_dau__lte=search, ngay_ket_thuc__gte=search)
    return render(request, "NghiPhep/search.html",
                  {"search_text": search, "form" : form, "NP_list" : danh_sach, 'nhan_vien': nhanvien, **ThongTinNP(request, nhanvien, nghiphep_all_nv, year)})

@login_required
def NP_delete (request,nghiphep_pk=None):
    if nghiphep_pk is not None:
        sach = get_object_or_404(NghiPhep, pk=nghiphep_pk)
        sach.delete()
    return redirect("DanhSachNP_NV")




@login_required()
def loc_don_nghi_phep_theo_trang_thai(request):
    year = request.GET.get('year')
    trang_thai=request.GET.get('trang_thai')
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    danh_sach = NghiPhep.objects.filter(nhan_vien=nhanvien, ngay_tao_don__year=year).order_by('-ngay_tao_don')
    danh_sach_don = NghiPhep.objects.filter(nhan_vien=nhanvien, trang_thai_don=trang_thai,ngay_tao_don__year=year).order_by('-ngay_tao_don')

    ThongTinNP(request, nhanvien, danh_sach, year)
    context = {
        'NP_list': danh_sach_don,
        'nhan_vien':nhanvien,
        **ThongTinNP(request, nhanvien, danh_sach, year)
    }
    return render(request, 'NghiPhep/FilterNP.html', context)


def DS_NV_quan_ly(request,nhanvien):
    year = request.GET.get('year')
    nhan_vien_quan_ly={}
    nhan_vien_BGH={}
    user = get_object_or_404(NhanVien, user=request.user)
    if nhanvien.chuc_vu == "Tổ trưởng":
        nhan_vien_quan_ly = NhanVien.objects.filter(to_phong_ban=nhanvien.to_phong_ban).exclude(id=nhanvien.id)
    elif nhanvien.chuc_vu =="Hiệu phó chuyên môn":
        nhan_vien_quan_ly = NhanVien.objects.filter(vi_tri_cong_viec__in=["Giáo viên", "Nhân sự", "Kế toán","Tuyển sinh"]).exclude(id=nhanvien.id)
    elif nhanvien.chuc_vu =="Hiệu phó hoạt động":
        nhan_vien_quan_ly = NhanVien.objects.filter(vi_tri_cong_viec__in=["Bếp", "Y - tế"]).exclude(id=nhanvien.id)
    elif nhanvien.chuc_vu =="Hiệu Trưởng":
        nhan_vien_BGH = NhanVien.objects.filter(vi_tri_cong_viec__in=["Hiệu phó chuyên môn", "Hiệu phó hoạt động"]).exclude(id=nhanvien.id)
        nhan_vien_quan_ly = NhanVien.objects.exclude(user=user.id)
    thong_tin = ThongTinNPYear(request, year)
    year = thong_tin['year']
    years=thong_tin['years']
    return {
        'year': year,
        'years': years,
        'nhan_vien_quan_ly': nhan_vien_quan_ly,
        'nhan_vien_BGH': nhan_vien_BGH
    }

def ThongTinNP_admin(request, nhanvien):
    nam = request.GET.get('year')
    thong_tin = ThongTinNPYear(request,nam)
    year = thong_tin['year']
    thong_tin = DS_NV_quan_ly(request, nhanvien)
    nhan_vien_quan_ly = thong_tin['nhan_vien_quan_ly']

    danh_sach = NghiPhep.objects.filter(nhan_vien__in=nhan_vien_quan_ly, ngay_tao_don__year=year)

    return {
        'year': year,
        'years': thong_tin['years'],
        'so_don': danh_sach.count(),
        'so_don_dang_duyet': danh_sach.filter(trang_thai_don='Đang chờ duyệt'),
        'so_don_da_duyet': danh_sach.filter(trang_thai_don='Đã duyệt'),
        'so_don_dang_bi_tu_choi': danh_sach.filter(trang_thai_don='Bị từ chối'),
    }



@login_required
def NghiPhep_list_admin(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    thong_tin = DS_NV_quan_ly(request, nhanvien)
    nhan_vien_quan_ly = thong_tin['nhan_vien_quan_ly']
    year=thong_tin['year']
    status_labels = ['Đang chờ duyệt', 'Đã duyệt', 'Bị từ chối']
    nghiphep_list = {}
    for status in status_labels:
        nghiphep_list[status] = NghiPhep.objects.filter(trang_thai_don=status, ngay_tao_don__year=year,
                                                        nhan_vien__in=nhan_vien_quan_ly).order_by('-ngay_tao_don')
    formghichu = Ghichu(request.GET)
    context = {
        'nghiphep':nghiphep_list,
        'nhan_vien': nhanvien,
        'formghichu': formghichu,
        'nhan_vien_quan_ly': nhan_vien_quan_ly,
        **DS_NV_quan_ly(request, nhanvien),
        **ThongTinNP_admin(request, nhanvien)
    }
    print("CTX nhan_vien obj:", context.get('nhan_vien'))
    return render(request, 'NghiPhep/NP_list_admin.html', context)

@login_required
def NghiPhep_list_hieutruong(request):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    thong_tin = DS_NV_quan_ly(request, nhanvien)
    nhan_vien_quan_ly = thong_tin['nhan_vien_BGH']
    year = request.GET.get('year')
    if year is None:
        year = now().year
    else:
        year = int(year)
    danh_sach = NghiPhep.objects.filter(nhan_vien__in=nhan_vien_quan_ly, ngay_tao_don__year=year).order_by('-ngay_tao_don')
    status_labels = ['Đang chờ duyệt', 'Đã duyệt', 'Bị từ chối']
    nghiphep_list = {}
    for status in status_labels:
        nghiphep_list[status] = NghiPhep.objects.filter(trang_thai_don=status, ngay_tao_don__year=year,
                                                        nhan_vien__in=nhan_vien_quan_ly).order_by('-ngay_tao_don')
    formghichu = Ghichu(request.GET)
    context = {
        'nghiphep': nghiphep_list,
        'formghichu': formghichu,
        **DS_NV_quan_ly(request, nhanvien),
        'so_don': danh_sach.count(),
        'so_don_dang_duyet': danh_sach.filter(trang_thai_don='Đang chờ duyệt'),
        'so_don_da_duyet': danh_sach.filter(trang_thai_don='Đã duyệt'),
        'so_don_dang_bi_tu_choi': danh_sach.filter(trang_thai_don='Bị từ chối'),
        'nhan_vien': nhanvien,
        'nhan_vien_quan_ly': nhan_vien_quan_ly,
    }
    return render(request, 'NghiPhep/NP_list_hieutruong.html', context)

def NP_nv_search_admin(request):
    nhan_vien = get_object_or_404(NhanVien, user=request.user)
    context = DS_NV_quan_ly(request, nhan_vien)
    nhan_vien_quan_ly = context['nhan_vien_quan_ly']
    nghiphep_list = {}
    search = ""
    form = SearchNVForm(request.GET or None)
    form.fields['nhan_vien'].queryset = nhan_vien_quan_ly
    if form.is_valid():
        search = form.cleaned_data.get("nhan_vien")
        if search:
            status_labels = ['Đang chờ duyệt', 'Đã duyệt', 'Bị từ chối']
            for status in status_labels:
                nghiphep_list[status] = NghiPhep.objects.filter(
                    trang_thai_don=status,
                    nhan_vien=search
                ).order_by('-ngay_tao_don')
    context.update({
        'search_text': search,
        'nghiphep': nghiphep_list,
        'nhan_vien': nhan_vien,
        'nhan_vien_quan_ly': nhan_vien_quan_ly,
    })
    return render(request, "NghiPhep/search_admin.html", context)


def NP_nv_search_hieutruong(request):
    nhan_vien = get_object_or_404(NhanVien, user=request.user)
    context = DS_NV_quan_ly(request, nhan_vien)
    nhan_vien_quan_ly = context['nhan_vien_BGH']
    form = SearchNVForm(request.GET or None)
    form.fields['nhan_vien'].queryset = nhan_vien_quan_ly
    nghiphep_list = {}
    search = ""
    if form.is_valid():
        search = form.cleaned_data.get("nhan_vien")
        if search:
            status_labels = ['Đang chờ duyệt', 'Đã duyệt', 'Bị từ chối']
            for status in status_labels:
                nghiphep_list[status] = NghiPhep.objects.filter(
                    trang_thai_don=status,
                    nhan_vien=search
                ).order_by('-ngay_tao_don')
    context.update({
        'search_text': search,
        'nghiphep': nghiphep_list,
        'nhan_vien': nhan_vien,
        'nhan_vien_quan_ly': nhan_vien_quan_ly,
    })
    return render(request, "NghiPhep/search_hieutruong.html", context)




@login_required()
def loc_don_nghi_phep_theo_trang_thai_admin(request):
    year = request.GET.get('year')
    trang_thai=request.GET.get('trang_thai')
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    thong_tin = DS_NV_quan_ly(request, nhanvien)
    nhan_vien = thong_tin['nhan_vien_quan_ly']
    danh_sach_don = {}
    danh_sach = NghiPhep.objects.filter(nhan_vien__in=nhan_vien, ngay_tao_don__year=year).order_by('-ngay_tao_don')
    danh_sach_don[trang_thai] = NghiPhep.objects.filter(nhan_vien__in=nhan_vien, trang_thai_don=trang_thai,ngay_tao_don__year=year).order_by('-ngay_tao_don')

    context = {
        'nghiphep': danh_sach_don,
        'nhan_vien':nhanvien,
        **DS_NV_quan_ly(request, nhanvien),
        **ThongTinNP_admin(request, nhanvien)
    }
    return render(request, 'NghiPhep/NP_list_admin.html', context)


@login_required()
def loc_don_nghi_phep_theo_trang_thai_hieutruong(request):
    year = request.GET.get('year')
    trang_thai=request.GET.get('trang_thai')
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    thong_tin = DS_NV_quan_ly(request, nhanvien)
    nhan_vien = thong_tin['nhan_vien_BGH']
    danh_sach_don = {}
    danh_sach = NghiPhep.objects.filter(nhan_vien__in=nhan_vien, ngay_tao_don__year=year).order_by('-ngay_tao_don')
    danh_sach_don[trang_thai] = NghiPhep.objects.filter(nhan_vien__in=nhan_vien, trang_thai_don=trang_thai,ngay_tao_don__year=year).order_by('-ngay_tao_don')

    context = {
        'nghiphep': danh_sach_don,
        'nhan_vien':nhanvien,
        **DS_NV_quan_ly(request, nhanvien),
        'so_don': danh_sach.count(),
        'so_don_dang_duyet': danh_sach.filter(trang_thai_don='Đang chờ duyệt'),
        'so_don_da_duyet': danh_sach.filter(trang_thai_don='Đã duyệt'),
        'so_don_dang_bi_tu_choi': danh_sach.filter(trang_thai_don='Bị từ chối'),
    }
    return render(request, 'NghiPhep/NP_list_hieutruong.html', context)





@login_required
def redirect_nghiphep_view(request):
    user = request.user
    if user.groups.filter(name='admin').exists():
        return redirect('DanhSachNP')  # tên URL của hàm NghiPhep_list_admin
    elif user.groups.filter(name='nhanvien').exists():
        return redirect('DanhSachNP_NV')  # tên URL của hàm NghiPhep_list_nv




@login_required
def EditNghiPhep (request, nghiphep_pk=None):
    year = request.GET.get('year')
    if year is None:
        year = now().year
    else:
        year = int(year)
    nhanvien = get_object_or_404(NhanVien, user = request.user)
    nghiphep_list_nv = NghiPhep.objects.filter(nhan_vien=nhanvien, ngay_tao_don__year=year).order_by('-ngay_tao_don')
    thong_tin = ThongTinNP(request, nhanvien, nghiphep_list_nv, year)
    pn_con_lai = thong_tin['PN_con_lai']
    if nghiphep_pk is not None:
        nghiphep = get_object_or_404(NghiPhep, pk=nghiphep_pk, nhan_vien=nhanvien)
    else:
        nghiphep = None
    if request.method == "POST": #ng dung submit
        form = NghiPhepForm(request.POST, instance=nghiphep)
        if form.is_valid():
            tt = form.cleaned_data
            start = tt.get('ngay_bat_dau')
            end = tt.get('ngay_ket_thuc')
            loai_nghi = tt.get('loai_nghi')
            if start and end:
                so_ngay_nghi = (end - start).days + 1
                if loai_nghi == 'Nghỉ phép năm' and so_ngay_nghi > pn_con_lai:
                    form.add_error(None,
                                   f"Số ngày nghỉ ({so_ngay_nghi}) vượt quá số ngày phép năm còn lại ({pn_con_lai}).")
                else:
                    updated_nghiphep = form.save(commit=False)
                    if nghiphep is None:
                        updated_nghiphep.nhan_vien = nhanvien
                        updated_nghiphep.ngay_tao_don = timezone.now()
                        updated_nghiphep.save()
                        return redirect("DanhSachNP_NV")
                    else :
                        updated_nghiphep.ngay_chinh_sua = timezone.now()
                        updated_nghiphep = form.save()
                        messages.success(request, "Đơn nghỉ phép {} được chỉnh sửa.".format(updated_nghiphep))
                        return redirect("DanhSachNP_NV")
    else:
        form = NghiPhepForm(instance=nghiphep)
    return render(request, "NghiPhep/formNghiPhep.html", {"model_type": "Nghỉ Phép", "form": form, "instance": nghiphep, "nhan_vien": nhanvien, **ThongTinNP(request, nhanvien, nghiphep_list_nv, year)})









def XulyNP(request, nghiphep_pk):
    nhanvien = get_object_or_404(NhanVien, user=request.user)
    nghiphep = get_object_or_404(NghiPhep, pk=nghiphep_pk)
    if request.method == "POST":
        form = Ghichu(request.POST)
        action = request.POST.get("action")
        if action == "tuchoi":
            if form.is_valid():
                ghi_chu = form.cleaned_data["ghi_chu"]
                if not ghi_chu.strip():
                    messages.error(request, "Vui lòng nhập lý do khi từ chối.")
                    return redirect("DanhSachNP")
                else:
                    nghiphep.trang_thai_don = "Bị từ chối"
                    nghiphep.ngay_duyet = timezone.now();
                    nghiphep.nguoi_duyet = nhanvien
                    nghiphep.ghi_chu = ghi_chu
                    nghiphep.save()

                    return redirect("DanhSachNP")
        elif action == "duyet":
            if form.is_valid():
                ghi_chu = form.cleaned_data["ghi_chu"]
                nghiphep.trang_thai_don = "Đã duyệt"
                nghiphep.ngay_duyet = timezone.now();
                nghiphep.ghi_chu = ghi_chu
                nghiphep.nguoi_duyet = nhanvien
                nghiphep.save()
                return redirect("DanhSachNP")
    else:
        form = Ghichu()
    return redirect("DanhSachNP")


