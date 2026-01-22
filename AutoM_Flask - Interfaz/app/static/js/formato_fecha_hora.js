let archivoGlobal = null;
let tokenDescarga = null;

function cargarColumnas() {
    archivoGlobal = document.getElementById("archivo").files[0];

    const fd = new FormData();
    fd.append("archivo", archivoGlobal);

    fetch("/formato/columnas", { method: "POST", body: fd })
        .then(r => r.json())
        .then(d => {
            const sel = document.getElementById("columnas");
            sel.innerHTML = "";
            d.columnas.forEach(c => {
                const o = document.createElement("option");
                o.value = c;
                o.textContent = c;
                sel.appendChild(o);
            });
        });
}

function ejecutar() {
    const fd = new FormData();
    fd.append("archivo", archivoGlobal);
    fd.append("columna", document.getElementById("columnas").value);

    fetch("/formato/ejecutar", { method: "POST", body: fd })
        .then(r => r.json())
        .then(d => {
            const out = document.getElementById("resultado");
            out.innerHTML = "";

            if (!d.ok) {
                out.textContent = d.error;
                return;
            }

            tokenDescarga = d.token;
            document.getElementById("btnDescargar").style.display = "inline";

            let html = `<b>Formato detectado:</b> ${d.formato}<br>`;
            html += `<b>Columnas creadas:</b> ${d.columnas.join(", ")}<br><br>`;

            html += "<table border='1' cellpadding='5'><tr>";
            Object.keys(d.preview[0]).forEach(k => {
                html += `<th>${k}</th>`;
            });
            html += "</tr>";

            d.preview.forEach(row => {
                html += "<tr>";
                Object.values(row).forEach(v => {
                    html += `<td>${v ?? ""}</td>`;
                });
                html += "</tr>";
            });

            html += "</table>";
            out.innerHTML = html;
        });
}

function descargar() {
    window.location.href = `/formato/descargar/${tokenDescarga}`;
}
