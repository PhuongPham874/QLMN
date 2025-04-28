from django.urls import path
from NghiPhep.views import NghiPhep_list_nv, NghiPhep, NP_nv_search, EditNghiPhep, NP_delete, NghiPhep_list_admin, \
    NP_nv_search_admin, XulyNP, redirect_nghiphep_view, loc_don_nghi_phep_theo_trang_thai, \
    loc_don_nghi_phep_theo_trang_thai_admin,  NghiPhep_list_hieutruong, \
    loc_don_nghi_phep_theo_trang_thai_hieutruong
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/NghiPhep/', redirect_nghiphep_view, name='DanhSachNP_redirect'),
    path('home/nhanvien/NghiPhep/', NghiPhep_list_nv, name='DanhSachNP_NV'), #nhanvien
    path('home/admin/NghiPhep/', NghiPhep_list_admin, name='DanhSachNP'), #admin
    path('home/hieutruong/NghiPhep/', NghiPhep_list_hieutruong, name='DanhSachNP_HT'),#hieutruong
    path('home/NghiPhep/Add', EditNghiPhep, name="AddNghiPhep"),
    path("home/NghiPhep/<int:nghiphep_pk>", EditNghiPhep, name="EditNghiPhep"),
    path('home/nhanvien/NghiPhepSearch/', NP_nv_search,name='TimKiemNP' ),
    path('home/admin/NghiPhepSearch/', NP_nv_search_admin,name='TimKiemNV' ),
    path("home/NghiPhep/xoa/<int:nghiphep_pk>", NP_delete, name="DeleteNghiPhep"),
    path("home/NghiPhep/XulyNP/<int:nghiphep_pk>", XulyNP, name="XulyNP"),
    path('home/nhanvien/don-nghi-phep/loc/', loc_don_nghi_phep_theo_trang_thai, name='loc_don_nghi_phep'),
    path('home/admin/don-nghi-phep/loc/', loc_don_nghi_phep_theo_trang_thai_admin, name='loc_don_nghi_phep_admin'),
    path('home/hieutruong/don-nghi-phep/loc/', loc_don_nghi_phep_theo_trang_thai_hieutruong, name='loc_don_nghi_phep_hieutruong'),
]
