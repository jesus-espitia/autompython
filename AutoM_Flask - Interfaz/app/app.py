from flask import Flask, render_template, request
import os

from routes.Top5_semanales import topDeInicidentes
from routes.descripcion_inc import descripcion_inc
from routes.comparar_infra import comparar_bp
from routes.accesos_criticos import accesos_b
from routes.formato_fecha_hora import formato_bp 

app = Flask(__name__)

# ==============================
# REGISTRAR BLUEPRINTS
# ==============================
app.register_blueprint(comparar_bp)
app.register_blueprint(accesos_b)
app.register_blueprint(formato_bp)

# ==============================
# MENÚ PRINCIPAL (CLAVE)
# ==============================
MODULOS_MENU = [
    {
        "nombre": "Top 5 Incidentes",
        "url": "/top5"
    },
    {
        "nombre": "Comparar Infra / AD",
        "url": "/comparar"
    },
    {
        "nombre": "Accesos Críticos",
        "url": "/accesos"
    },
    {
        "nombre": "Separar Fecha y Hora",
        "url": "/formato"
    }
]

# ==============================
# RUTA PRINCIPAL
# ==============================
@app.route("/")
def index():
    return render_template("index.html", modulos=MODULOS_MENU)

# ==============================
# TOP 5
# ==============================
@app.route("/top5", methods=["GET", "POST"])
def top5():
    reporte = ""

    if request.method == "POST":
        file = request.files.get("archivo_csv")
        if file:
            ruta = os.path.join("CSVPasado", file.filename)
            os.makedirs("CSVPasado", exist_ok=True)
            file.save(ruta)
            reporte = topDeInicidentes(ruta)

    return render_template("top5_semanales.html", reporte=reporte)

# ==============================
# DESCRIPCIÓN INC
# ==============================
@app.route("/descripcion_inc", methods=["POST"])
def aplicar_descripcion():
    texto = request.form.get("reporte", "")
    return descripcion_inc(texto)

# ==============================
# COMPARAR
# ==============================
@app.route("/comparar")
def comparar():
    return render_template("comparar_infra.html")

# ==============================
# ACCESOS
# ==============================
@app.route("/accesos")
def accesos():
    return render_template("accesos_criticos.html")

# ==============================
# FORMATO FECHA / HORA
# ==============================
@app.route("/formato")
def formato():
    return render_template("formato_fecha_hora.html")

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
