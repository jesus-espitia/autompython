document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");

    if (!searchInput) return;

    const filas = Array.from(document.querySelectorAll(".tabla-incidentes tbody tr"));

    searchInput.addEventListener("keyup", function () {

        const filtro = searchInput.value.toLowerCase().trim();
        let coincidencias = 0;

        filas.forEach(function (fila) {

            const textoFila = fila.textContent.toLowerCase();

            if (textoFila.includes(filtro)) {

                fila.style.display = "";

                coincidencias++;

                resaltarCoincidencias(fila, filtro);

            } else {

                fila.style.display = "none";

            }

        });

    });

});


function resaltarCoincidencias(fila, filtro) {

    if (filtro === "") {
        limpiarResaltado(fila);
        return;
    }

    const celdas = fila.querySelectorAll("td");

    celdas.forEach(function (celda) {

        const textoOriginal = celda.textContent;

        const regex = new RegExp(`(${filtro})`, "gi");

        if (textoOriginal.toLowerCase().includes(filtro)) {

            celda.innerHTML = textoOriginal.replace(regex, "<mark>$1</mark>");

        } else {

            celda.textContent = textoOriginal;

        }

    });

}


function limpiarResaltado(fila) {

    const celdas = fila.querySelectorAll("td");

    celdas.forEach(function (celda) {

        celda.textContent = celda.textContent;

    });

}


function copiarAnalisis() {

    const texto = document.body.getAttribute("data-analisis");

    if (!texto) {
        alert("No hay análisis disponible");
        return;
    }

    navigator.clipboard.writeText(texto)
        .then(() => alert("Análisis copiado"));

}


function confirmarEliminacion() {
    return confirm("¿Estás seguro de que deseas eliminar este archivo?");
}