document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");

    if (!searchInput) return;

    // Busca dentro de TODOS los contenedores .buscadores
    const contenedores = document.querySelectorAll(".buscadores");

    searchInput.addEventListener("keyup", function () {

        const filtro = searchInput.value.toLowerCase().trim();

        contenedores.forEach(function (contenedor) {

            // Soporta tablas
            const filas = contenedor.querySelectorAll("tbody tr");

            // Soporta cards, divs, etc
            const elementos = contenedor.querySelectorAll("div, li, tr");

            const items = filas.length > 0 ? filas : elementos;

            items.forEach(function (item) {

                const texto = item.textContent.toLowerCase();

                if (texto.includes(filtro)) {
                    item.style.display = "";
                    resaltarCoincidencias(item, filtro);
                } else {
                    item.style.display = "none";
                }

            });

        });

    });

});

function resaltarCoincidencias(elemento, filtro) {

    if (filtro === "") {
        limpiarResaltado(elemento);
        return;
    }

    const nodos = elemento.querySelectorAll("td, div, span, li");

    nodos.forEach(function (nodo) {

        const textoOriginal = nodo.textContent;
        const regex = new RegExp(`(${filtro})`, "gi");

        if (textoOriginal.toLowerCase().includes(filtro)) {
            nodo.innerHTML = textoOriginal.replace(regex, "<mark>$1</mark>");
        } else {
            nodo.textContent = textoOriginal;
        }

    });

}

function limpiarResaltado(elemento) {

    const nodos = elemento.querySelectorAll("td, div, span, li");

    nodos.forEach(function (nodo) {
        nodo.textContent = nodo.textContent;
    });

}