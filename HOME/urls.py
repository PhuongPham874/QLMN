from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import home_view, login_view, logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', home_view, name='home'),
    path("login/", login_view, name="login"),
    path('logout/', logout_view,name='logout' ),

]