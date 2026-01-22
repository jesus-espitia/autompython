document.getElementById("btnDescripcion").addEventListener("click", () => {
    const textarea = document.getElementById("reporte");

    fetch("/descripcion_inc", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "reporte=" + encodeURIComponent(textarea.value)
    })
    .then(res => res.text())
    .then(data => {
        textarea.value = data;
    });
});
