import os

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from QLMN.settings import BASE_DIR
from .views import home_view, login_view, logout_view, change_password
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', home_view, name='home'),
    path("login/", login_view, name="login"),
    path('logout/', logout_view,name='logout' ),
    path('doi-mat-khau/', change_password, name='change_password')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))