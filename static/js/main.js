'use strict';

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("searchForm");
    const input = document.getElementById("searchInput");

    if (form && input) {
            form.addEventListener("submit", function (e) {
                if (input.value.trim() === "") {
                    e.preventDefault();
                    input.classList.add("is-invalid");
                } else {
                    input.classList.remove("is-invalid");
                }
        });
    }

    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollTopBtn.style.display = 'flex';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });
    }


    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    if (toastElList.length) {
        toastElList.forEach(function (toastEl) {
            const toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 3000
            });
            toast.show();
        });
    }
});
