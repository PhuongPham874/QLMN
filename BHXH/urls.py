from django.urls import path
from .views import *
urlpatterns = [
    path('bhxh/',bhxh,name='bhxh_list'),
    path('addbhxh/',themmoiBHXH,name='add_bhxh'),
    path('editbhxh/<int:ma_nv>',chinhsuaBHXH,name='edit_bhxh'),
    path('infobhxh/<int:ma_nv>',thongtinchitiet,name='info_bhxh'),
    # path('noptien/',dong_bhxh,name='nop_tien'),
    path('ajax/tinh-tien-bhxh/', tinh_tien_bhxh_ajax, name='tinh_tien_bhxh_ajax'),
    path('home/BHXH',redirect_bhxh_view,name='redirectBHXH'),
    path('bhxhcuatoi/', bhxh_cua_toi, name='bhxh_me'),
#

]