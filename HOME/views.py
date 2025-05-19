#Trang LOGIN
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.messages import get_messages

from HOME.models import NhanVien


def login_view(request):

    storage = get_messages(request)  # Xóa messages cũ trước khi render
    for _ in storage:
        pass  # Duyệt qua storage để nó bị xóa

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
            return redirect("login")  # Chuyển hướng để tránh resubmit form

        login(request, user)
        return redirect("home")  # Điều hướng sau khi đăng nhập thành công

    return render(request, "login.html")
# Trang HOME
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    nhanvien = NhanVien.objects.get(user=request.user)
    return render(request, 'home.html',{
        'nhan_vien' : nhanvien
    })
#Trang LOGOUT
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Đảm bảo session auth không bị logout
            messages.success(request, 'Mật khẩu của bạn đã được thay đổi thành công!')
            return redirect('home')  # Điều hướng sau khi đổi mật khẩu thành công
        else:
            messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'changepassword.html', {
        'form': form
    })

