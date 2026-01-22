let archivoGlobal = null;

function cargarColumnas() {
    const input = document.getElementById("archivo");
    const archivo = input.files[0];

    if (!archivo) {
        alert("Selecciona un archivo");
        return;
    }

    archivoGlobal = archivo;

    const formData = new FormData();
    formData.append("archivo", archivo);

    fetch("/accesos/columnas", {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (!data.ok) {
            alert(data.error);
            return;
        }

        const select = document.getElementById("columnas");
        select.innerHTML = "";

        data.columnas.forEach(col => {
            const opt = document.createElement("option");
            opt.value = col;
            opt.textContent = col;
            select.appendChild(opt);
        });
    });
}

function ejecutar() {
    if (!archivoGlobal) {
        alert("Primero carga un archivo");
        return;
    }

    const columna = document.getElementById("columnas").value;
    const guardar = document.getElementById("guardar").checked;

    const formData = new FormData();
    formData.append("archivo", archivoGlobal);
    formData.append("columna", columna);
    formData.append("guardar", guardar);

    fetch("/accesos/ejecutar", {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        const salida = document.getElementById("resultado");

        if (!data.ok) {
            salida.textContent = data.error;
            return;
        }

        let texto = data.mensaje + "\n\n";

        if (data.archivo_resultado) {
            texto += "📄 Archivo generado:\n" + data.archivo_resultado + "\n";
        }

        if (data.archivo_guardado) {
            texto += "\n💾 Archivo original guardado:\n" + data.archivo_guardado;
        }

        salida.textContent = texto;
    });
}

function ejecutar() {
    if (!archivoGlobal) {
        alert("Primero carga un archivo");
        return;
    }

    const columna = document.getElementById("columnas").value;
    const guardar = document.getElementById("guardar").checked;

    const formData = new FormData();
    formData.append("archivo", archivoGlobal);
    formData.append("columna", columna);
    formData.append("guardar", guardar);

    fetch("/accesos/ejecutar", {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        const salida = document.getElementById("resultado");

        if (!data.ok) {
            salida.textContent = data.error;
            return;
        }

        let texto = `
✔️ ${data.mensaje}

Total registros: ${data.total_registros}
Accesos críticos: ${data.criticos}

`;

        if (data.criticos === 0) {
            texto += "No se encontraron accesos críticos.";
            salida.textContent = texto;
            return;
        }

        texto += "Primeros resultados:\n\n";

        data.datos.forEach((fila, i) => {
            texto += `#${i + 1}\n`;
            for (const k in fila) {
                texto += `${k}: ${fila[k]}\n`;
            }
            texto += "\n";
        });

        if (data.archivo_guardado) {
            texto += `\n💾 Archivo original guardado: ${data.archivo_guardado}`;
        }

        salida.textContent = texto;
    });
}

