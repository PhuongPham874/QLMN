// (Giữ nguyên các hàm filter đã có ở đầu file...)

document.addEventListener("DOMContentLoaded", function () {
    const hash = window.location.hash;

    if (hash) {
        const trigger = document.querySelector(`a[href="${hash}"]`);
        if (trigger) {
            new bootstrap.Tab(trigger).show();
        }
    }

    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(el => {
        el.addEventListener('shown.bs.tab', function (e) {
            const newHash = e.target.getAttribute('href');
            if (history.pushState) {
                history.pushState(null, null, newHash);
            } else {
                location.hash = newHash;
            }
        });
    });
});
