from django.urls import path
from .views import khen_thuong_list, add_khen_thuong, xoa_khen_thuong, khen_thuong_cua_toi, edit_khen_thuong, duyet_khen_thuong, khen_thuong_cho_duyet

urlpatterns = [
    path('home/admin/khen-thuong/', khen_thuong_list, name='khen_thuong_list'),
    path('khen-thuong/add/', add_khen_thuong, name='add_khen_thuong'),
    path('khen-thuong/xoa/<int:reward_id>/', xoa_khen_thuong, name='xoa_khen_thuong'),
    path('home/NV/khen-thuong-cua-toi/', khen_thuong_cua_toi, name='khen_thuong_cua_toi'),
    path('khen-thuong/edit/<int:reward_id>/', edit_khen_thuong, name='edit_khen_thuong'),
    path('khen-thuong/duyet/<int:reward_id>/', duyet_khen_thuong, name='duyet_khen_thuong'),
    path('khen-thuong/cho-duyet/', khen_thuong_cho_duyet, name='khen_thuong_cho_duyet'),
]