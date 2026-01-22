const archivoInput = document.getElementById("archivo");
const btnColumnas = document.getElementById("btnColumnas");
const columnas = document.getElementById("columnas");
const btnEjecutar = document.getElementById("btnEjecutar");
const resultado = document.getElementById("resultado");
const chkGuardar = document.getElementById("guardar");

let archivoActual = null;

btnColumnas.onclick = () => {
    if (!archivoInput.files.length) {
        resultado.value = "⚠️ Selecciona un archivo";
        return;
    }

    archivoActual = archivoInput.files[0];

    const fd = new FormData();
    fd.append("archivo", archivoActual);

    fetch("/comparar/columnas", { method: "POST", body: fd })
        .then(r => r.json())
        .then(d => {
            if (!d.ok) {
                resultado.value = d.error;
                return;
            }

            columnas.innerHTML = "";
            d.columnas.forEach(c => {
                const o = document.createElement("option");
                o.value = c;
                o.textContent = c;
                columnas.appendChild(o);
            });

            columnas.disabled = false;
            btnEjecutar.disabled = false;
        });
};

btnEjecutar.onclick = () => {
    const fd = new FormData();
    fd.append("archivo", archivoActual);
    fd.append("columna", columnas.value);
    fd.append("guardar", chkGuardar.checked);

    resultado.value = "⏳ Procesando...";

    fetch("/comparar/ejecutar", { method: "POST", body: fd })
        .then(r => r.json())
        .then(d => {
            if (!d.ok) {
                resultado.value = d.error;
                return;
            }

            resultado.value = d.resultado;

            if (d.archivo_guardado) {
                resultado.value += "\n\n📁 Archivo guardado: " + d.archivo_guardado;
            }
        });
};
