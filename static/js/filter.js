// Hàm lọc kỷ luật của tôi
function filterKyLuatCuaToi(event) {
    event.preventDefault();
    const thang = document.getElementById('thang_ky_luat_toi').value;
    const nam = document.getElementById('nam_ky_luat_toi').value;
    const items = document.querySelectorAll('#ky-luat-cua-toi-list .ky-luat-item');
    const noDataMessage = document.querySelector('#ky-luat-cua-toi .no-data-message');

    let hasVisibleItems = false;

    items.forEach(item => {
        const date = item.getAttribute('data-date');
        let show = true;

        if (thang && nam) {
            const filterDate = `${nam}-${thang.padStart(2, '0')}`;
            show = date === filterDate;
        } else if (nam) {
            show = date.startsWith(nam);
        } else if (thang) {
            show = date.endsWith(`-${thang.padStart(2, '0')}`);
        }

        item.style.display = show ? '' : 'none';
        if (show) hasVisibleItems = true;
    });

    if (noDataMessage) {
        noDataMessage.style.display = hasVisibleItems ? 'none' : 'block';
    }
}

// Hàm lọc kỷ luật của nhân viên
function filterKyLuatNhanVien(event) {
    event.preventDefault();
    const nhanVien = document.getElementById('nhan_vien_ky_luat').value;
    const thang = document.getElementById('thang_ky_luat_nhan_vien').value;
    const nam = document.getElementById('nam_ky_luat_nhan_vien').value;
    const items = document.querySelectorAll('#ky-luat-nhan-vien-list .ky-luat-item');
    const noDataMessage = document.querySelector('#ky-luat-cua-nhan-vien .no-data-message');

    let hasVisibleItems = false;

    items.forEach(item => {
        const date = item.getAttribute('data-date');
        const nhanVienId = item.getAttribute('data-nhan-vien');
        let show = true;

        if (nhanVien) {
            show = nhanVienId === nhanVien;
        }
        if (thang && nam && show) {
            const filterDate = `${nam}-${thang.padStart(2, '0')}`;
            show = date === filterDate;
        } else if (nam && show) {
            show = date.startsWith(nam);
        } else if (thang && show) {
            show = date.endsWith(`-${thang.padStart(2, '0')}`);
        }

        item.style.display = show ? '' : 'none';
        if (show) hasVisibleItems = true;
    });

    if (noDataMessage) {
        noDataMessage.style.display = hasVisibleItems ? 'none' : 'block';
    }
}

// Hàm lọc khen thưởng của tôi
function filterKhenThuongCuaToi(event) {
    event.preventDefault();
    const thang = document.getElementById('thang_khen_thuong_toi').value;
    const nam = document.getElementById('nam_khen_thuong_toi').value;
    const items = document.querySelectorAll('#khen-thuong-cua-toi-list .khen-thuong-item');
    const noDataMessage = document.querySelector('#khen-thuong-cua-toi .no-data-message');

    let hasVisibleItems = false;

    items.forEach(item => {
        const date = item.getAttribute('data-date');
        let show = true;

        if (thang && nam) {
            const filterDate = `${nam}-${thang.padStart(2, '0')}`;
            show = date === filterDate;
        } else if (nam) {
            show = date.startsWith(nam);
        } else if (thang) {
            show = date.endsWith(`-${thang.padStart(2, '0')}`);
        }

        item.style.display = show ? '' : 'none';
        if (show) hasVisibleItems = true;
    });

    if (noDataMessage) {
        noDataMessage.style.display = hasVisibleItems ? 'none' : 'block';
    }
}

// Hàm lọc khen thưởng của nhân viên
function filterKhenThuongNhanVien(event) {
    event.preventDefault();
    const nhanVien = document.getElementById('nhan_vien_khen_thuong').value;
    const thang = document.getElementById('thang_khen_thuong_nhan_vien').value;
    const nam = document.getElementById('nam_khen_thuong_nhan_vien').value;
    const items = document.querySelectorAll('#khen-thuong-nhan-vien-list .khen-thuong-item');
    const noDataMessage = document.querySelector('#khen-thuong-cua-nhan-vien .no-data-message');

    let hasVisibleItems = false;

    items.forEach(item => {
        const date = item.getAttribute('data-date');
        const nhanVienId = item.getAttribute('data-nhan-vien');
        let show = true;

        if (nhanVien) {
            show = nhanVienId === nhanVien;
        }
        if (thang && nam && show) {
            const filterDate = `${nam}-${thang.padStart(2, '0')}`;
            show = date === filterDate;
        } else if (nam && show) {
            show = date.startsWith(nam);
        } else if (thang && show) {
            show = date.endsWith(`-${thang.padStart(2, '0')}`);
        }

        item.style.display = show ? '' : 'none';
        if (show) hasVisibleItems = true;
    });

    if (noDataMessage) {
        noDataMessage.style.display = hasVisibleItems ? 'none' : 'block';
    }
}

// Thêm sự kiện cho các select box và form
document.addEventListener('DOMContentLoaded', () => {
    // Gắn sự kiện cho form lọc
    const forms = [
        { id: 'ky-luat-cua-toi-filter', handler: filterKyLuatCuaToi },
        { id: 'ky-luat-nhan-vien-filter', handler: filterKyLuatNhanVien },
        { id: 'khen-thuong-cua-toi-filter', handler: filterKhenThuongCuaToi },
        { id: 'khen-thuong-nhan-vien-filter', handler: filterKhenThuongNhanVien }
    ];

    forms.forEach(form => {
        const formElement = document.getElementById(form.id);
        if (formElement) {
            formElement.addEventListener('submit', form.handler);
            // Gắn sự kiện onchange cho các select box
            const selects = formElement.querySelectorAll('select');
            selects.forEach(select => {
                select.addEventListener('change', form.handler);
            });
        }
    });

    // Handle main tabs
    const mainTabs = document.querySelectorAll('#mainTabs .nav-link');
    const mainContents = document.querySelectorAll('#mainTabs ~ .tab-content');

    mainTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = tab.getAttribute('data-tab');

            // Update active tab
            mainTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show/hide content
            mainContents.forEach(content => {
                content.classList.toggle('active', content.id === targetId);
            });
        });
    });

    // Handle sub tabs for Kỷ luật
    const kyLuatTabs = document.querySelectorAll('#kyLuatTabs .nav-link');
    const kyLuatContents = document.querySelectorAll('#danh-sach-ky-luat .tab-content');

    kyLuatTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = tab.getAttribute('data-tab');

            // Update active tab
            kyLuatTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show/hide content
            kyLuatContents.forEach(content => {
                content.classList.toggle('active', content.id === targetId);
            });
        });
    });

    // Handle sub tabs for Khen thưởng
    const rewardTabs = document.querySelectorAll('#rewardTabs .nav-link');
    const rewardContents = document.querySelectorAll('#danh-sach-khen-thuong .tab-content');

    rewardTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = tab.getAttribute('data-tab');

            // Update active tab
            rewardTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show/hide content
            rewardContents.forEach(content => {
                content.classList.toggle('active', content.id === targetId);
            });
        });
    });
});