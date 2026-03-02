document.addEventListener('DOMContentLoaded', function() {
    
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('toggleBtn');
    const navItems = document.querySelectorAll('.nav-item');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function(event) {
            event.stopPropagation(); 
            sidebar.classList.toggle('active');
        });
    }

    if (mainContent && sidebar) {
        mainContent.addEventListener('click', function() {
            if (sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    navItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }

            if (href === '#' || href === '' || href === 'javascript:void(0)') {
                e.preventDefault();
            }
            navItems.forEach(function(nav) {
                nav.classList.remove('active');
            });
            this.classList.add('active');
        });
    });


    function setActivePage() {
        const currentPage = window.location.pathname.split('/').pop();

        navItems.forEach(function(item) {
            const itemHref = item.getAttribute('href');
            
            if (itemHref === currentPage) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    setActivePage();

    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.boxShadow = '0 0 0 2px rgba(255, 208, 0, 0.3)';
        });
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.boxShadow = 'none';
        });
    }
});