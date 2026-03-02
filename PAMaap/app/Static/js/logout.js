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