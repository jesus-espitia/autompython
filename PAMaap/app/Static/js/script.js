document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Seleccionamos los elementos necesarios
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('toggleBtn');
    const navItems = document.querySelectorAll('.nav-item');

    // 2. Función para abrir/cerrar el menú en móviles
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function(event) {
            // IMPORTANTE: Detiene la propagación del clic para que no active el cierre inmediato
            event.stopPropagation(); 
            
            sidebar.classList.toggle('active');
        });
    }

    // 3. Cerrar el menú si se hace clic FUERA del sidebar (en el contenido principal)
    if (mainContent && sidebar) {
        mainContent.addEventListener('click', function() {
            // Solo intentamos cerrar si el menú está abierto
            if (sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // 4. Lógica para marcar el elemento activo en el menú
    navItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            // Prevenimos el salto del enlace "#"
            e.preventDefault();

            // Quitamos la clase 'active' de todos los elementos
            navItems.forEach(function(nav) {
                nav.classList.remove('active');
            });
            
            // Agregamos la clase 'active' solo al elemento clickeado
            this.classList.add('active');

            // Si estamos en móvil, cerramos el menú después de seleccionar
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }
        });
    });

    // 5. Simple validación visual para el input de búsqueda (opcional)
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