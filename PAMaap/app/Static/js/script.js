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

document.addEventListener("DOMContentLoaded", function () {

    const cards = document.querySelectorAll(".adjustable-card");

    cards.forEach(card => {
        card.addEventListener("click", function (e) {

            const url = this.getAttribute("href");

            if (!url || url === "#") return;

            e.preventDefault();

            let title = "¿Continuar?";
            let text = "¿Deseas entrar a esta función?";

            if (url.includes("comparacionArchivos")) {
                title = "📂 Comparación de Archivos";
                text = "Se seleccionará un archivo y una columna específica para comparar información de servidores. El sistema analizará los datos y clasificará los resultados en diferentes categorías (Infraestructura, AD y Otros), facilitando la identificación de diferencias. Además, podrás copiar los resultados generados para su uso posterior.";
            }

            else if (url.includes("reportes")) {
                title = "📊 Análisis de Incidentes (Top 5)";
                text = "Se seleccionará un archivo para analizar los incidentes registrados. El sistema identificará los 5 servidores con mayor cantidad de incidentes, mostrando información detallada como responsable, tipo y ubicación. Además, podrás visualizar el detalle de los incidentes filtrados y copiar un resumen del análisis generado.";
            }

            else if (url.includes("archivoVisualizar")) {
                title = "🗂️ Gestión de Alimentadores";
                text = "Se seleccionará un archivo para visualizar su contenido en formato de tabla editable. Podrás agregar o eliminar filas y columnas, así como modificar la información directamente. Finalmente, tendrás la opción de guardar los cambios realizados en el archivo.";
            }

            else if (url.includes("UnificarArchivos")) {
                title = "📦 Unificación y Generación de Reporte Mensual";
                text = "Se seleccionará un mes para procesar y unificar múltiples archivos relacionados. El sistema consolidará la información y generará automáticamente un reporte completo, el cual será descargado en formato ZIP para su uso y distribución.";
            }

            else if (url.includes("")) {
                title = "";
                text = "";
            }

            else if (url.includes("")) {
                title = "";
                text = "";
            }

            Swal.fire({
                title: title,
                text: text,
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Sí, continuar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = url;
                }
            });

        });
    });

});