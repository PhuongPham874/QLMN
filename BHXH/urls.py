from django.urls import path
from .views import *
urlpatterns = [
    path('bhxh/',bhxh,name='bhxh_list'),
    path('addbhxh/',themmoiBHXH,name='add_bhxh'),
    path('editbhxh/<int:ma_nv>',chinhsuaBHXH,name='edit_bhxh'),
    path('infobhxh/<int:ma_nv>',thongtinchitiet,name='info_bhxh'),
    path('noptien/',dong_bhxh,name='nop_tien')
]