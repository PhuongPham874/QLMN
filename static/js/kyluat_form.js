document.addEventListener('DOMContentLoaded', function() {
    // Lấy các phần tử DOM
    const mucDoSelect = document.getElementById('id_muc_do');
    const soTienPhatContainer = document.getElementById('so_tien_phat_container');
    const soTienPhatInput = document.getElementById('id_so_tien_phat');
    const minhChungFileInput = document.getElementById('id_minh_chung_file');
    const minhChungUrlInput = document.getElementById('id_minh_chung_url');
    const minhChungFileContainer = document.getElementById('minh_chung_file_container');
    const minhChungUrlContainer = document.getElementById('minh_chung_url_container');
    const ngayBatDauInput = document.getElementById('id_ngay_bat_dau');
    const ngayKetThucInput = document.getElementById('id_ngay_ket_thuc');

    // Hàm kiểm tra định dạng URL
    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    // Hàm kiểm tra file hợp lệ
    function isValidFile(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        const maxSize = 5 * 1024 * 1024; // 5MB
        return file && allowedTypes.includes(file.type) && file.size <= maxSize;
    }

    // Hàm hiển thị/ẩn trường số tiền phạt
    function toggleSoTienPhat() {
        if (mucDoSelect.value === 'PHAT_TIEN') {
            soTienPhatContainer.style.display = 'flex';
            soTienPhatInput.removeAttribute('disabled');
            soTienPhatInput.setAttribute('required', 'required');
        } else {
            soTienPhatContainer.style.display = 'none';
            soTienPhatInput.setAttribute('disabled', 'disabled');
            soTienPhatInput.removeAttribute('required');
            soTienPhatInput.value = ''; // Xóa giá trị để không gửi dữ liệu rỗng
        }
    }

    // Hàm áp dụng thuộc tính required cho minh chứng
    function toggleMinhChungRequired() {
        const isRequired = mucDoSelect.value === 'KY_LUAT_3_THANG' || mucDoSelect.value === 'KY_LUAT_6_THANG';
        minhChungFileInput.required = isRequired && !minhChungUrlInput.value.trim();
        minhChungUrlInput.required = isRequired && !minhChungFileInput.files.length;
        minhChungFileContainer.classList.toggle('required', isRequired);
        minhChungUrlContainer.classList.toggle('required', isRequired);
    }

    // Hàm xử lý logic chỉ cho phép một loại minh chứng
    function handleMinhChungInputs() {
        const hasFile = minhChungFileInput.files.length > 0;
        const hasUrl = minhChungUrlInput.value.trim() !== '';

        if (hasFile) {
            if (!isValidFile(minhChungFileInput.files[0])) {
                alert('Vui lòng chọn file PDF hoặc hình ảnh (JPG/PNG) có kích thước dưới 5MB.');
                minhChungFileInput.value = '';
                minhChungFileInput.focus();
                return;
            }
            minhChungUrlInput.value = '';
            minhChungUrlInput.setAttribute('disabled', 'disabled');
        } else {
            minhChungUrlInput.removeAttribute('disabled');
        }

        if (hasUrl) {
            if (!isValidUrl(minhChungUrlInput.value)) {
                alert('Vui lòng nhập URL hợp lệ (bắt đầu bằng http:// hoặc https://).');
                minhChungUrlInput.value = '';
                minhChungUrlInput.focus();
                return;
            }
            minhChungFileInput.value = '';
            minhChungFileInput.setAttribute('disabled', 'disabled');
        } else {
            minhChungFileInput.removeAttribute('disabled');
        }

        toggleMinhChungRequired();
    }

    // Hàm tự động tính ngày kết thúc
    function updateNgayKetThuc() {
        const mucDo = mucDoSelect.value;
        const ngayBatDau = ngayBatDauInput.value;

        if (!ngayBatDau || !(mucDo === 'KY_LUAT_3_THANG' || mucDo === 'KY_LUAT_6_THANG')) {
            ngayKetThucInput.value = '';
            ngayKetThucInput.removeAttribute('required');
            return;
        }

        const date = new Date(ngayBatDau);
        if (isNaN(date.getTime())) {
            alert('Vui lòng nhập ngày bắt đầu hợp lệ (định dạng YYYY-MM-DD).');
            ngayBatDauInput.value = '';
            ngayKetThucInput.value = '';
            ngayBatDauInput.focus();
            return;
        }

        const months = mucDo === 'KY_LUAT_3_THANG' ? 3 : 6;
        date.setMonth(date.getMonth() + months);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        ngayKetThucInput.value = `${year}-${month}-${day}`;
        ngayKetThucInput.setAttribute('required', 'required');
    }

    // Kiểm tra trước khi gửi form
    document.querySelector('form').addEventListener('submit', function(e) {
        if (mucDoSelect.value === 'PHAT_TIEN' && (!soTienPhatInput.value || parseFloat(soTienPhatInput.value) <= 0)) {
            e.preventDefault();
            alert('Vui lòng nhập số tiền phạt lớn hơn 0.');
            soTienPhatInput.focus();
            return;
        }

        const isRequired = mucDoSelect.value === 'KY_LUAT_3_THANG' || mucDoSelect.value === 'KY_LUAT_6_THANG';
        if (isRequired && !minhChungFileInput.files.length && !minhChungUrlInput.value.trim()) {
            e.preventDefault();
            alert('Vui lòng cung cấp ít nhất một minh chứng (file hoặc URL) cho kỷ luật 3 tháng hoặc 6 tháng.');
            minhChungFileInput.focus();
            return;
        }

        if (minhChungFileInput.files.length && !isValidFile(minhChungFileInput.files[0])) {
            e.preventDefault();
            alert('File không hợp lệ. Vui lòng chọn file PDF hoặc hình ảnh (JPG/PNG) dưới 5MB.');
            minhChungFileInput.focus();
            return;
        }

        if (minhChungUrlInput.value.trim() && !isValidUrl(minhChungUrlInput.value)) {
            e.preventDefault();
            alert('URL không hợp lệ. Vui lòng nhập URL hợp lệ (bắt đầu bằng http:// hoặc https://).');
            minhChungUrlInput.focus();
            return;
        }

        if (isRequired && !ngayKetThucInput.value) {
            e.preventDefault();
            alert('Vui lòng nhập ngày kết thúc hợp lệ cho kỷ luật 3 tháng hoặc 6 tháng.');
            ngayKetThucInput.focus();
            return;
        }
    });

    // Khởi tạo trạng thái ban đầu
    toggleSoTienPhat();
    toggleMinhChungRequired();
    handleMinhChungInputs();
    updateNgayKetThuc();

    // Thêm sự kiện cho các input
    mucDoSelect.addEventListener('change', () => {
        toggleSoTienPhat();
        toggleMinhChungRequired();
        updateNgayKetThuc();
        handleMinhChungInputs();
    });

    ngayBatDauInput.addEventListener('change', updateNgayKetThuc);
    minhChungFileInput.addEventListener('change', handleMinhChungInputs);
    minhChungUrlInput.addEventListener('input', handleMinhChungInputs);

    // Xử lý khi chỉnh sửa
    if (minhChungFileInput.value || minhChungUrlInput.value) {
        handleMinhChungInputs();
    }
});