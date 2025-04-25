import csv
import re
from datetime import datetime
from unidecode import unidecode
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from HOME.models import NhanVien, HopDongLaoDong, BHXH, NghiPhep, KyLuat, KhenThuong, ChamCong, DONGBHXH, PhuCap, PhuCapNhanVien


class Command(BaseCommand):
    help = 'Load employee management data from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str)

    @staticmethod
    def convert_date(date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%m/%d/%Y').date()
        except ValueError:
            return None

    @staticmethod
    def generate_username(full_name):
        return unidecode(full_name).replace(" ", "").lower()

    @staticmethod
    def row_to_dict(row, header):
        if len(row) < len(header):
            row += [''] * (len(header) - len(row))
        return dict([(header[i], row[i]) for i, head in enumerate(header) if head])

    def handle(self, *args, **options):
        m = re.compile(r'content:\s*(\w+)')

        header = None
        models = dict()
        try:
            with open(options['csv'], encoding='utf-8-sig') as csvfile:
                model_data = csv.reader(csvfile)
                model_name = None
                for i, row in enumerate(model_data):
                    print(f"Row {i}: {row}")  # Debug
                    if max([len(cell.strip()) for cell in row[1:] + ['']]) == 0 and m.match(row[0]):
                        print(f"Detected model: {model_name}")  # Debug
                        model_name = m.match(row[0]).groups()[0]
                        models[model_name] = []
                        header = None
                        continue

                    if header is None:
                        header = row
                        continue
                    if model_name is None:
                        raise CommandError(f"Model name is missing or invalid in row {i}: {row}")

                    row_dict = self.row_to_dict(row, header)
                    if set(row_dict.values()) == {''}:
                        continue
                    models[model_name].append(row_dict)
        except FileNotFoundError:
            raise CommandError('File "{}" does not exist'.format(options['csv']))

        # Process NhanVien
        for data_dict in models.get('NhanVien', []):
            username = self.generate_username(data_dict['ten_nv'])
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': data_dict['ten_nv'].split()[-1],
                'last_name': " ".join(data_dict['ten_nv'].split()[:-1]),
                'email': data_dict['email'],
                'is_staff': True,
                'is_active': True
            })
            user.set_password('123456789')
            user.save()

            nv, created = NhanVien.objects.get_or_create(user=user, defaults={
                'ten_nv': data_dict['ten_nv'],
                'gioi_tinh': data_dict['gioi_tinh'],
                'ngay_sinh': self.convert_date(data_dict['ngay_sinh']),
                'anh_ca_nhan': data_dict['anh_ca_nhan'],
                'so_cccd': data_dict['so_cccd'],
                'so_dien_thoai': data_dict['so_dien_thoai'],
                'vi_tri_cong_viec': data_dict['vi_tri_cong_viec'],
                'chuc_vu': data_dict['chuc_vu'],
                'to_phong_ban': data_dict['to_phong_ban'],
                'trinh_do_hoc_van': data_dict['trinh_do_hoc_van'],
                'chuyen_nganh': data_dict.get('chuyen_nganh'),
                'noi_dao_tao': data_dict['noi_dao_tao'],
                'nam_tn': data_dict.get('nam_tn'),
                'ngay_cap': self.convert_date(data_dict['ngay_cap']),
                'noi_cap': data_dict['noi_cap'],
                'dia_chi_tam_tru': data_dict['dia_chi_tam_tru'],
            })

        # Process HopDongLaoDong
        for data_dict in models.get('HopDongLaoDong', []):
            HopDongLaoDong.objects.get_or_create(nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                                                 vi_tri_lam_viec=data_dict['vi_tri_lam_viec'],
                                                 to_phong_ban=data_dict['to_phong_ban'],
                                                 trang_thai_hop_dong=data_dict['trang_thai_hop_dong'],
                                                 loai_hop_dong=data_dict['loai_hop_dong'],
                                                 luong=float(data_dict['luong'].replace(',', '').strip()),
                                                 ngay_ky=self.convert_date(data_dict['ngay_ky']),
                                                 tu_ngay=self.convert_date(data_dict['tu_ngay']),
                                                 den_ngay=self.convert_date(data_dict['den_ngay']))

        # Process BHXH
        for data_dict in models.get('BHXH', []):
            BHXH.objects.get_or_create(nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                                       nhan_vien_dong=data_dict['nhan_vien_dong'],
                                       truong_dong=data_dict['truong_dong'],
                                       ma_BHXH=data_dict['ma_BHXH'],
                                       thoi_gian_bat_dau=self.convert_date(data_dict['thoi_gian_bat_dau']))

        # Process NghiPhep
        for data_dict in models.get('NghiPhep', []):
            NghiPhep.objects.get_or_create(nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                                           loai_nghi=data_dict['loai_nghi'],
                                           ngay_bat_dau=self.convert_date(data_dict['ngay_bat_dau']),
                                           ngay_ket_thuc=self.convert_date(data_dict['ngay_ket_thuc']),
                                           ly_do=data_dict['ly_do'],
                                           trang_thai_don=data_dict['trang_thai_don'],
                                           ghi_chu=data_dict.get('ghi_chu', ''),
                                            nguoi_duyet = NhanVien.objects.get(id=int(data_dict['nguoi_duyet'])),
                                            ngay_duyet = self.convert_date(data_dict['ngay_duyet']),
                                            ngay_tao_don = self.convert_date(data_dict['ngay_tao_don']),
                                            ngay_chinh_sua = self.convert_date(data_dict['ngay_chinh_sua']))

        # Process KyLuat
        for data_dict in models.get('KyLuat', []):
            try:
                so_tien_phat_value = data_dict.get('so_tien_phat')
                if so_tien_phat_value == '':
                    so_tien_phat_value = None
                else:
                    try:
                        so_tien_phat_value = float(so_tien_phat_value.replace(',', '').strip())
                    except ValueError:
                        print(f"Lỗi chuyển đổi so_tien_phat: {data_dict['so_tien_phat']}")
                        so_tien_phat_value = None

                KyLuat.objects.get_or_create(nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                                             ngay_bat_dau=self.convert_date(data_dict['ngay_bat_dau']),
                                             ngay_ket_thuc=self.convert_date(data_dict['ngay_ket_thuc']),
                                             ly_do=data_dict['ly_do'],
                                             nguoi_tao_don_id=data_dict['nguoi_tao_don'],
                                             muc_do=data_dict['muc_do'],
                                             so_tien_phat=so_tien_phat_value,
                                             nguoi_duyet_don_id=data_dict.get('nguoi_duyet_don'),
                                             trang_thai=data_dict['trang_thai'],
                                             minh_chung_url=data_dict.get('minh_chung_url'),
                                             minh_chung_file=data_dict['minh_chung_file']
                                             )
            except Exception as e:
                print(f"Lỗi khi xử lý KyLuat: {e}")
                print(f"Dữ liệu gây lỗi: {data_dict}")

        # Process KhenThuong
        for data_dict in models.get('KhenThuong', []):
            KhenThuong.objects.get_or_create(nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                                         ngay_tao=self.convert_date(data_dict['ngay_tao']),
                                         gia_tri=float(data_dict['gia_tri']),
                                         ly_do=data_dict['ly_do'],
                                         trang_thai=data_dict['trang_thai'],
                                         nguoi_tao_don_id=data_dict['nguoi_tao_don'],
                                         nguoi_xac_nhan_id=data_dict.get('nguoi_duyet_don'),
                                         minh_chung_url=data_dict.get('minh_chung_url'),
                                         minh_chung_file=data_dict['minh_chung_file'])


        # Process ChamCong
        for data_dict in models.get('ChamCong', []):
            ChamCong.objects.get_or_create(
                nhan_vien=NhanVien.objects.get(id=int(data_dict['id_nv'])),
                gio_vao=data_dict['gio_vao'] if data_dict['gio_vao'] else None,
                gio_ra=data_dict['gio_ra'] if data_dict['gio_ra'] else None,
                ngay=int(data_dict['ngay']),
                thang=int(data_dict['thang']),
                nam=int(data_dict['nam']),
                trang_thai=int(data_dict['trang_thai'])
            )


        # Process DongBHXH
        for data_dict in models.get('DongBHXH', []):
            DONGBHXH.objects.get_or_create(
                nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                ngay_bat_dau=self.convert_date(data_dict['ngay_bat_dau']),
                ngay_ket_thuc=self.convert_date(data_dict['ngay_ket_thuc']),
                tong_tien=float(data_dict['tong_tien'])
            )

        for data_dict in models.get('PhuCap', []):
            PhuCap.objects.get_or_create(
                ten_phu_cap=data_dict['ten_phu_cap'],
                gia_tri=float(data_dict['gia_tri'])
            )

        for data_dict in models.get('PhuCapNhanVien', []):
            PhuCapNhanVien.objects.get_or_create(
                nhan_vien=NhanVien.objects.get(id=int(data_dict['nhan_vien'])),
                phu_cap=PhuCap.objects.get(id=int(data_dict['phu_cap_id'])),
            )

        print("Import complete")