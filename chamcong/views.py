from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from HOME.models import NhanVien, ChamCong

@login_required
def cham_cong_view(request):
    if request.user.is_superuser:
        # Nếu là superuser, lấy danh sách tất cả nhân viên
        nhan_vien = get_object_or_404(NhanVien, user=request.user)
        nhan_viens = NhanVien.objects.all().order_by('id')  # Sắp xếp theo 'id' hoặc trường khác
        return render(request, 'ChamCong/danh_sach_nhan_vien.html', {
            'is_super': True,
            'nhan_viens': nhan_viens,
            'nhan_vien': nhan_vien
        })

    # Nếu là user thường → xử lý như cũ
    nhan_vien = get_object_or_404(NhanVien, user=request.user)
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

    # Sắp xếp các tháng/năm từ mới đến cũ
    sorted_cham_cong_theo_thang = sorted(
        cham_cong_theo_thang.items(),
        key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])),
        reverse=True
    )

    # Sắp xếp tháng và năm để hiển thị
    months = sorted(all_months)
    years = sorted(all_years)

    return render(request, 'ChamCong/cham_cong.html', {
        'is_super': False,
        'nhan_vien': nhan_vien,
        'cham_cong_theo_thang': sorted_cham_cong_theo_thang,
        'months': months,
        'years': years
    })


import cv2
import time
import os
from deepface import DeepFace
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from HOME.models import ChamCong, NhanVien
from datetime import datetime
from django.utils import timezone
import win32gui
import win32con

# Đường dẫn đến thư mục dataset
dataset_path = r"C:\Users\HP\Desktop\LTW\Dataset"

# Hàm đặt cửa sổ OpenCV lên trên cùng
def set_window_always_on_top(window_name="Webcam"):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

@login_required
def cham_cong_bang_khuon_mat(request):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return JsonResponse({"message": "❌ Không thể mở webcam"}, status=400)

    print("📸 Webcam đã mở. Chuẩn bị nhận diện sau 3 giây...")
    start_time = time.time()
    detection_started = False

    result_message = "❌ Không nhận diện được khuôn mặt"
    recognized = False
    nhan_vien_id = None

    while True:
        ret, frame = cap.read()
        if not ret:
            result_message = "❌ Không thể đọc frame từ webcam"
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

                    # Lấy ID từ folder cha
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
                result_message = f"❌ Lỗi nhận diện: {str(e)}"
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
            now = timezone.localtime(timezone.now())

            ngay = now.day
            thang = now.month
            nam = now.year
            gio_vao = now.time()

            # Xác định trạng thái
            if gio_vao.hour < 8 or (gio_vao.hour == 8 and gio_vao.minute <= 0):
                trang_thai = 0  # Đúng giờ
            else:
                trang_thai = 2  # Muộn

            cham_cong, created = ChamCong.objects.get_or_create(
                nhan_vien=nhan_vien,
                ngay=ngay,
                thang=thang,
                nam=nam,
                defaults={
                    'gio_vao': gio_vao,
                    'trang_thai': trang_thai
                }
            )

            if not created:
                return JsonResponse({"message": f"🟡 Nhân viên ID {nhan_vien_id} đã chấm công hôm nay rồi."})

            return JsonResponse({"message": f"🟢 Chấm công thành công cho nhân viên ID {nhan_vien_id}"})

        except NhanVien.DoesNotExist:
            return JsonResponse({"message": f"❌ Không tìm thấy nhân viên ID {nhan_vien_id} trong hệ thống"}, status=404)

    return JsonResponse({"message": result_message}, status=400)