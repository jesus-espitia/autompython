function guardarArchivo() {
    const data = obtenerDatosTabla();

    data.archivo = document.querySelector("h2").innerText.replace("Archivo: ", "");

    fetch("/funcion/archivoVisualizar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(r => {
        if (r.status === "ok") {
            alert("✅ Guardado correctamente");
        } else {
            alert("❌ " + r.msg);
        }
    });
}