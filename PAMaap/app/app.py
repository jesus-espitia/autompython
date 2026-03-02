from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__, template_folder="Templates", static_folder="Static")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "archives")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


# =========================
# RUTAS PRINCIPALES
# =========================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/configuracion")
def configuracion():
    return render_template("configuracion.html")


@app.route("/mi_ficha")
def mi_ficha():
    return render_template("mi_ficha.html")


@app.route("/documentos")
def documentos():
    archivos = []

    for nombre in os.listdir(app.config["UPLOAD_FOLDER"]):
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)

        if os.path.isfile(ruta):
            tamaño = os.path.getsize(ruta)
            fecha = os.path.getctime(ruta)

            archivos.append({
                "nombre": nombre,
                "tamano": round(tamaño / 1024, 2),
                "fecha": datetime.fromtimestamp(fecha).strftime("%d %b %Y")
            })

    return render_template("documentos.html", archivos=archivos)


# =========================
# VER ARCHIVO (abrir en navegador)
# =========================

@app.route("/ver/<nombre>")
def ver_documento(nombre):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nombre)


# =========================
# DESCARGAR ARCHIVO
# =========================

@app.route("/descargar/<nombre>")
def descargar_documento(nombre):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nombre, as_attachment=True)


# =========================
# ELIMINAR ARCHIVO
# =========================

@app.route("/eliminar/<nombre>", methods=["POST"])
def eliminar_documento(nombre):
    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)

    if os.path.exists(ruta):
        os.remove(ruta)

    return redirect(url_for("documentos"))


# =========================
# SUBIR ARCHIVO
# =========================

@app.route("/subir_documento", methods=["POST"])
def subir_documento():
    if "archivo" not in request.files:
        return redirect(url_for("documentos"))

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return redirect(url_for("documentos"))

    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_final = f"{fecha_actual}_{archivo.filename}"

    ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_final)
    archivo.save(ruta_guardado)

    return redirect(url_for("documentos"))


if __name__ == "__main__":
    app.run(debug=True)