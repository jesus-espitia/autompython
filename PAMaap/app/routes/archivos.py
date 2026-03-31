from flask import render_template, redirect, url_for, session, send_file, abort, request, jsonify
import os
import re
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "archives")

ALIMENTADORES_PATH = os.path.join(
    UPLOAD_FOLDER,
    "XLXS_IMPORT",
    "ALIMENTADORES"
)

os.makedirs(ALIMENTADORES_PATH, exist_ok=True)


# =========================
# LISTAR ARCHIVOS
# =========================
def F_archivoVisualizar():
    if "user" not in session:
        return redirect(url_for("login"))

    archivos = []
    columnas = []
    datos = []
    archivo_actual = None

    # =========================
    # LISTAR ARCHIVOS
    # =========================
    if os.path.exists(ALIMENTADORES_PATH):
        for file in os.listdir(ALIMENTADORES_PATH):
            ruta = os.path.join(ALIMENTADORES_PATH, file)

            if os.path.isfile(ruta) and file.endswith(".xlsx"):
                archivos.append({"nombre": file})

    # =========================
    # ABRIR ARCHIVO (GET)
    # =========================
    nombre_archivo = request.args.get("archivo")

    if nombre_archivo:
        ruta = os.path.join(ALIMENTADORES_PATH, nombre_archivo)

        if os.path.exists(ruta):
            try:
                df = pd.read_excel(ruta, dtype=str)
                columnas = df.columns.tolist()
                datos = df.fillna("").to_dict(orient="records")
                archivo_actual = nombre_archivo
            except Exception as e:
                return f"Error leyendo archivo: {str(e)}"

    # =========================
    # GUARDAR CAMBIOS (POST)
    # =========================
    if request.method == "POST":
        data = request.json

        nombre_archivo = data.get("archivo")
        columnas = data.get("columnas", [])
        filas = data.get("filas", [])

        ruta = os.path.join(ALIMENTADORES_PATH, nombre_archivo)

        if not os.path.exists(ruta):
            return jsonify({"status": "error", "msg": "Archivo no existe"})

        try:
            df = pd.DataFrame(filas, columns=columnas)
            df.to_excel(ruta, index=False)

            return jsonify({"status": "ok"})

        except Exception as e:
            return jsonify({"status": "error", "msg": str(e)})

    return render_template(
        "F_archivoVisualizar.html",
        archivos=archivos,
        columnas=columnas,
        datos=datos,
        archivo=archivo_actual
    )