"""
URL configuration for QLMN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from QLMN import settings
from QLMN.settings import BASE_DIR

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('HOME.urls')),
    path('', include('NghiPhep.urls')),
    path('', include('KhenThuong.urls')),
    path('', include('KyLuat.urls')),
    path('', include('BHXH.urls')),
    path('', include('HoSo.urls')),
    path('', include('luong.urls')),
    path('', include('chamcong.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))
