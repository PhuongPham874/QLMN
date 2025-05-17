
from django.urls import path
from . import views

urlpatterns = [
    path('chamcong/', views.cham_cong_view, name='cham_cong'),
    path('chamcong/nhanvien/<int:nhanvien_id>/', views.cham_cong_view, name='cham_cong_theo_nhanvien'),
    path('cham-cong-bang-khuon-mat/', views.cham_cong_bang_khuon_mat, name='cham_cong_bang_khuon_mat'),
]

