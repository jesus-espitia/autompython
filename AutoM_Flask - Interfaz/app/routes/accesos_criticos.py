import os
import re
import pandas as pd
from flask import Blueprint, request, jsonify
from datetime import datetime

accesos_b = Blueprint("accesos", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ARCHIVOS_GUARDADOS = os.path.join(BASE_DIR, "ArchivosGuardados")
os.makedirs(ARCHIVOS_GUARDADOS, exist_ok=True)

# ==================================================
# 🧠 LECTOR UNIVERSAL
# ==================================================
def leer_archivo(archivo):
    ext = os.path.splitext(archivo.filename)[1].lower()
    archivo.stream.seek(0)

    if ext == ".csv":
        return pd.read_csv(archivo, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")

    if ext in (".xlsx", ".xls"):
        return pd.read_excel(archivo)

    raise ValueError("Formato no soportado")

# ==================================================
# 📌 COLUMNAS
# ==================================================
@accesos_b.route("/accesos/columnas", methods=["POST"])
def recolectar_columnas():
    archivo = request.files.get("archivo")

    if not archivo:
        return jsonify(ok=False, error="No se recibió archivo")

    df = leer_archivo(archivo)

    return jsonify(ok=True, columnas=df.columns.tolist())

# ==================================================
# 🚨 EJECUTAR
# ==================================================
@accesos_b.route("/accesos/ejecutar", methods=["POST"])
def ejecutar():
    try:
        archivo = request.files.get("archivo")
        columna = request.form.get("columna")
        guardar = request.form.get("guardar") == "true"

        if not archivo or not columna:
            return jsonify(ok=False, error="Datos incompletos")

        df = leer_archivo(archivo)

        if columna not in df.columns:
            return jsonify(ok=False, error="La columna no existe")

        # ================================
        # DETECCIÓN
        # ================================
        valores_criticos = ("DOMAIN USER", "EVERYONE")

        df_tmp = df.copy()
        df_tmp[columna] = df_tmp[columna].astype(str).str.upper().str.strip()

        patron = "|".join(map(re.escape, valores_criticos))
        df_criticos = df_tmp[df_tmp[columna].str.contains(patron, na=False)]

        # ================================
        # GUARDAR ORIGINAL (OPCIONAL)
        # ================================
        archivo_guardado = None
        if guardar:
            ruta = os.path.join(ARCHIVOS_GUARDADOS, archivo.filename)
            archivo.stream.seek(0)
            archivo.save(ruta)
            archivo_guardado = archivo.filename

        # ================================
        # RESPUESTA (SIEMPRE A INTERFAZ)
        # ================================
        return jsonify(
            ok=True,
            mensaje="Análisis completado",
            total_registros=len(df),
            criticos=len(df_criticos),
            columnas=df_criticos.columns.tolist(),
            datos=df_criticos.head(200).to_dict(orient="records"),
            archivo_guardado=archivo_guardado
        )

    except Exception as e:
        return jsonify(ok=False, error=str(e))
