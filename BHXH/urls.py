from django.urls import path
from .views import *
urlpatterns = [
    path('bhxh/', bhxh, name='bhxh_list'),
    path('addbhxh/', themmoiBHXH, name='add_bhxh'),
    path('editbhxh/<int:ma_nv>/', chinhsuaBHXH, name='edit_bhxh'),
    path('thong-tin-bhxh/', thong_tin_bhxh, name='thong_tin_bhxh'),
]