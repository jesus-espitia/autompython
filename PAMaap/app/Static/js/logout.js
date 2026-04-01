document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("userNameToggle");
    const dropdown = document.getElementById("userDropdown");

    toggle.addEventListener("click", () => {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
        if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = "none";
        }
    });
});

const toggle = document.getElementById('userNameToggle');
const dropdown = document.getElementById('userDropdown');

toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('show');
});

document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && e.target !== toggle) {
        dropdown.classList.remove('show');
    }
});

dropdown.querySelector('a').addEventListener('click', (e) => {
    e.stopPropagation();
});