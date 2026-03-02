document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Seleccionamos los elementos necesarios
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('toggleBtn');
    const navItems = document.querySelectorAll('.nav-item');

    // 2. Función para abrir/cerrar el menú en móviles
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function(event) {
            event.stopPropagation(); 
            sidebar.classList.toggle('active');
        });
    }

    // 3. Cerrar el menú si se hace clic FUERA del sidebar
    if (mainContent && sidebar) {
        mainContent.addEventListener('click', function() {
            if (sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // 4. Lógica de Navegación y Estado Activo
    navItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            // Obtenemos la ruta del atributo href
            const href = this.getAttribute('href');

            // CERRAR MENÚ MÓVIL: Si estamos en móvil, cerramos el sidebar al hacer clic
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }

            if (href === '#' || href === '' || href === 'javascript:void(0)') {
                e.preventDefault();
            }
            // NOTA: No necesitamos 'else' porque si no prevenimos el default, el navegador sigue el link.

            // LÓGICA VISUAL (Opcional para transición suave antes de cargar la nueva página)
            navItems.forEach(function(nav) {
                nav.classList.remove('active');
            });
            this.classList.add('active');
        });
    });


    function setActivePage() {
        // Obtenemos el nombre del archivo actual (ej: "mi_ficha.html" o "/")
        const currentPage = window.location.pathname.split('/').pop();

        navItems.forEach(function(item) {
            const itemHref = item.getAttribute('href');
            
            // Si el item del menú coincide con la página actual, le ponemos la clase active
            if (itemHref === currentPage) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // Ejecutamos la función al cargar la página
    setActivePage();

    // 6. Efecto visual para el input de búsqueda
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