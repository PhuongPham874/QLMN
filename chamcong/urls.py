from django.urls import path
from .views import cham_cong

urlpatterns = [
    path('cham-cong/', cham_cong, name='cham_cong'),
]