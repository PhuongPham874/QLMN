from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from HOME.models import NhanVien, ChamCong
from django.utils import timezone
import time

@login_required
def cham_cong_view(request, nhanvien_id=None):
    current_user = get_object_or_404(NhanVien, user=request.user)

    # Nếu là nhân sự và nhấn vào một nhân viên cụ thể
    if current_user.vi_tri_cong_viec == 'Nhân sự' and nhanvien_id:
        nhan_vien = get_object_or_404(NhanVien, id=nhanvien_id)
    else:
        nhan_vien = current_user

    # Nếu là nhân sự và không chọn nhân viên → hiện danh sách
    if current_user.vi_tri_cong_viec == 'Nhân sự' and nhanvien_id is None:
        nhan_viens = NhanVien.objects.all().order_by('id')
        now = timezone.now()

        nhan_viens_data = []
        for nv in nhan_viens:
            cham_cong = ChamCong.objects.filter(
                nhan_vien=nv,
                ngay=now.day,
                thang=now.month,
                nam=now.year
            ).first()

            nhan_viens_data.append({
                'nhan_vien': nv,
                'gio_vao': cham_cong.gio_vao if cham_cong else None,
                'gio_ra': cham_cong.gio_ra if cham_cong else None,
            })

        return render(request, 'ChamCong/danh_sach_nhan_vien.html', {
            'nhan_viens_data': nhan_viens_data,
            'nhan_vien': current_user
        })

    # Xử lý hiển thị lịch sử chấm công cho nhân viên cụ thể
    cham_cong_data = ChamCong.objects.filter(nhan_vien=nhan_vien)

    cham_cong_theo_thang = {}
    all_months = set()
    all_years = set()

    for record in cham_cong_data:
        year = record.nam
        month = record.thang
        day = record.ngay

        year_month = f"{year}-{month:02d}"
        if year_month not in cham_cong_theo_thang:
            cham_cong_theo_thang[year_month] = {}
        cham_cong_theo_thang[year_month][day] = record

        all_months.add(month)
        all_years.add(year)

    sorted_cham_cong_theo_thang = sorted(
        cham_cong_theo_thang.items(),
        key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])),
        reverse=True
    )

    months = sorted(all_months)
    years = sorted(all_years)

    return render(request, 'ChamCong/cham_cong.html', {
        'is_super': current_user.vi_tri_cong_viec == 'Nhân sự',
        'nhan_vien': nhan_vien,
        'cham_cong_theo_thang': sorted_cham_cong_theo_thang,
        'months': months,
        'years': years
    })
import cv2
import time
import os
from deepface import DeepFace
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from HOME.models import ChamCong, NhanVien
from datetime import datetime
from django.utils import timezone
import win32gui
import win32con

# Đường dẫn đến thư mục dataset
dataset_path = r"C:\Users\HP\Desktop\LTW\Dataset"

def set_window_always_on_top(window_name="Webcam"):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

@login_required
def cham_cong_bang_khuon_mat(request):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messages.error(request, "❌ Không thể mở webcam.")
        return redirect("danh_sach_nhan_vien")

    print("📸 Webcam đã mở. Chuẩn bị nhận diện sau 3 giây...")
    start_time = time.time()
    detection_started = False

    recognized = False
    nhan_vien_id = None

    while True:
        ret, frame = cap.read()
        if not ret:
            messages.error(request, "❌ Không thể đọc frame từ webcam.")
            break

        elapsed = time.time() - start_time

        if not detection_started and elapsed < 3:
            remaining = int(3 - elapsed)
            cv2.putText(frame, f"Chuan bi nhan dien: {remaining}s", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            detection_started = True
            try:
                result = DeepFace.find(img_path=frame, db_path=dataset_path, enforce_detection=True)

                if len(result) > 0 and len(result[0]) > 0:
                    identity_path = result[0].iloc[0]["identity"]
                    nhan_vien_folder = os.path.basename(os.path.dirname(identity_path))
                    nhan_vien_id = int(nhan_vien_folder)
                    recognized = True

                    cv2.putText(frame, f"Thanh cong, ID: {nhan_vien_id}", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Webcam", frame)
                    set_window_always_on_top("Webcam")
                    cv2.waitKey(3000)
                    break
                else:
                    cv2.putText(frame, "Khong nhan ra", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            except Exception as e:
                print("❌ Lỗi nhận diện:", e)
                messages.error(request, f"❌ Lỗi nhận diện: {str(e)}")
                break

        cv2.imshow("Webcam", frame)
        set_window_always_on_top("Webcam")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if recognized and nhan_vien_id:
        try:
            nhan_vien = NhanVien.objects.get(id=nhan_vien_id)
            now = timezone.now()

            ngay = now.day
            thang = now.month
            nam = now.year
            current_time = now.time()

            cham_cong, created = ChamCong.objects.get_or_create(
                nhan_vien=nhan_vien,
                ngay=ngay,
                thang=thang,
                nam=nam,
                defaults={
                    'gio_vao': current_time,
                    'trang_thai': 0 if current_time.hour < 8 or (current_time.hour == 8 and current_time.minute <= 0) else 2
                }
            )

            if created:
                messages.success(request, f"🟢 Chấm công thành công cho nhân viên ID {nhan_vien_id} (Giờ vào).")
            else:
                if cham_cong.gio_ra is None:
                    cham_cong.gio_ra = current_time
                    cham_cong.save()
                    messages.success(request, f"🔵 Đã cập nhật giờ ra cho nhân viên ID {nhan_vien_id}.")
                else:
                    messages.warning(request, f"🟡 Nhân viên ID {nhan_vien_id} đã chấm công đầy đủ hôm nay.")
        except NhanVien.DoesNotExist:
            messages.error(request, f"❌ Không tìm thấy nhân viên ID {nhan_vien_id} trong hệ thống")
    elif not recognized:
        messages.error(request, "❌ Không nhận diện được khuôn mặt.")

    return redirect("cham_cong")
