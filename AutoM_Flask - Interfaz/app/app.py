from flask import Flask, render_template, request
import os

from routes.Top5_semanales import topDeInicidentes
from routes.descripcion_inc import descripcion_inc
from routes.comparar_infra import comparar_bp
from routes.accesos_criticos import accesos_b

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
RUTA_MODULOS = os.path.join(BASE_DIR, "routes")

# ==============================
# REGISTRAR BLUEPRINTS
# ==============================
app.register_blueprint(comparar_bp)
app.register_blueprint(accesos_b)

# ==============================
# LISTAR MÓDULOS
# ==============================
def listar_modulos():
    return [
        f[:-3] for f in os.listdir(RUTA_MODULOS)
        if f.endswith(".py") and not f.startswith("__")
    ]

# ==============================
# RUTA PRINCIPAL
# ==============================
@app.route("/")
def index():
    modulos = listar_modulos()
    return render_template("index.html", modulos=modulos)

# ==============================
# TOP 5
# ==============================
@app.route("/top5", methods=["GET", "POST"])
def top5():
    reporte = ""

    if request.method == "POST":
        file = request.files.get("archivo_csv")

        if file:
            csv_dir = os.path.join(BASE_DIR, "CSVPasado")
            os.makedirs(csv_dir, exist_ok=True)

            ruta = os.path.join(csv_dir, file.filename)
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
# COMPARAR INFRA / AD
# ==============================
@app.route("/comparar")
def comparar():
    return render_template("comparar_infra.html")

# ==============================
# ACCESOS CRÍTICOS
# ==============================
@app.route("/accesos")
def accesos():
    return render_template("accesos_criticos.html")

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
