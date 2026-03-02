document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");
    const documentsList = document.querySelector(".documents-list");
    const noResults = document.getElementById("noResults");

    if (!searchInput) return;

    const docItems = Array.from(document.querySelectorAll(".doc-item"));

    searchInput.addEventListener("keyup", function () {

        const filtro = searchInput.value.toLowerCase().trim();
        let coincidencias = 0;

        docItems.forEach(function (doc) {

            const nombre = doc.getAttribute("data-nombre");
            const fecha = doc.getAttribute("data-fecha");
            const tamano = doc.getAttribute("data-tamano");

            const coincide =
                nombre.includes(filtro) ||
                fecha.includes(filtro) ||
                tamano.includes(filtro);

            if (coincide) {
                doc.style.display = "flex";
                coincidencias++;
            } else {
                doc.style.display = "none";
            }

            // 🔥 Resaltado inteligente
            const nombreElemento = doc.querySelector(".doc-name");
            const nombreOriginal = doc.getAttribute("data-nombre");

            if (filtro !== "" && nombre.includes(filtro)) {
                const regex = new RegExp(`(${filtro})`, "gi");
                nombreElemento.innerHTML =
                    nombreOriginal.replace(regex, "<mark>$1</mark>");
            } else {
                nombreElemento.textContent = nombreOriginal;
            }

        });

        // 🔥 Mostrar mensaje si no hay resultados
        if (coincidencias === 0) {
            noResults.style.display = "block";
        } else {
            noResults.style.display = "none";
        }

        // 🔥 Reordenar mostrando coincidencias arriba
        docItems.sort(function (a, b) {
            const aVisible = a.style.display !== "none";
            const bVisible = b.style.display !== "none";
            return bVisible - aVisible;
        });

        docItems.forEach(function (doc) {
            documentsList.appendChild(doc);
        });

    });

});

function confirmarEliminacion() {
    return confirm("¿Estás seguro de que deseas eliminar este archivo?");
}