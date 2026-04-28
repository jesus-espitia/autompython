let estadoInicial = null;

function capturarEstadoInicial() {
    estadoInicial = JSON.stringify(obtenerDatosTabla());
}


window.addEventListener("load", () => {
    setTimeout(capturarEstadoInicial, 500);
});


function hayCambios() {
    const actual = JSON.stringify(obtenerDatosTabla());
    return actual !== estadoInicial;
}


window.addEventListener("beforeunload", function (e) {
    if (hayCambios()) {
        e.preventDefault();
        e.returnValue = "";
    }
});


function agregarFila() {
    const tbody = document.querySelector("#tabla tbody");
    const numColumnas = document.querySelectorAll("#tabla thead th").length - 1;

    const fila = document.createElement("tr");

    for (let i = 0; i < numColumnas; i++) {
        const celda = document.createElement("td");
        celda.contentEditable = "true";
        fila.appendChild(celda);
    }

    const accion = document.createElement("td");
    accion.innerHTML = '<button onclick="eliminarFila(this)">❌</button>';
    fila.appendChild(accion);

    tbody.appendChild(fila);
}


function eliminarFila(btn) {
    if (confirm("¿Eliminar esta fila?")) {
        btn.closest("tr").remove();
    }
}


function agregarColumna() {
    const nombre = prompt("Nombre de la nueva columna:");
    if (!nombre) return;

    const theadRow = document.querySelector("#tabla thead tr");
    const th = document.createElement("th");
    th.contentEditable = "true";
    th.innerText = nombre;

    theadRow.insertBefore(th, theadRow.lastElementChild);

    document.querySelectorAll("#tabla tbody tr").forEach(tr => {
        const td = document.createElement("td");
        td.contentEditable = "true";
        tr.insertBefore(td, tr.lastElementChild);
    });
}


function eliminarColumna() {
    const columnas = document.querySelectorAll("#tabla thead th");

    if (columnas.length <= 2) {
        alert("Debe haber al menos una columna");
        return;
    }

    const nombre = prompt("Nombre de la columna a eliminar:");
    if (!nombre) return;

    let index = -1;

    columnas.forEach((col, i) => {
        if (col.innerText.trim() === nombre.trim()) {
            index = i;
        }
    });

    if (index === -1) {
        alert("Columna no encontrada");
        return;
    }

    if (!confirm(`¿Eliminar columna "${nombre}"?`)) return;

    columnas[index].remove();

    document.querySelectorAll("#tabla tbody tr").forEach(tr => {
        tr.children[index].remove();
    });
}

function obtenerDatosTabla() {
    let columnas = [];
    let filas = [];

    const headers = document.querySelectorAll("#tabla thead th");

    headers.forEach((th, i) => {
        if (i < headers.length - 1) {
            columnas.push(th.innerText.trim());
        }
    });

    document.querySelectorAll("#tabla tbody tr").forEach(tr => {
        let fila = {};
        let celdas = tr.querySelectorAll("td");

        columnas.forEach((col, i) => {
            fila[col] = celdas[i].innerText.trim();
        });

        filas.push(fila);
    });

    return { columnas, filas };
}

function guardarArchivo() {

    if (!hayCambios()) {
        alert("⚠️ No hay cambios para guardar");
        return;
    }

    if (!confirm("¿Guardar cambios?")) return;

    const data = obtenerDatosTabla();

    // 🔥 Obtener nombre del archivo desde el HTML
    const archivo = document.querySelector("h2")?.innerText.replace("Archivo: ", "").trim();

    if (!archivo) {
        alert("❌ No se pudo identificar el archivo");
        return;
    }

    const payload = {
        archivo: archivo,
        columnas: data.columnas,
        filas: data.filas
    };

    fetch(`/funcion/archivoVisualizar`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(response => {
        if (response.status === "ok") {
            alert("✅ Archivo guardado correctamente");
            capturarEstadoInicial();
        } else {
            alert("❌ Error: " + response.msg);
        }
    })
    .catch(err => {
        alert("❌ Error de conexión");
        console.error(err);
    });
}