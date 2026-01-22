import os
import re
import uuid
import pandas as pd
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from collections import Counter

formato_bp = Blueprint("formato", __name__, url_prefix="/formato")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp_resultados")
os.makedirs(TEMP_DIR, exist_ok=True)

# =========================
# LECTOR
# =========================
def leer_archivo(archivo):
    ext = os.path.splitext(archivo.filename)[1].lower()
    archivo.stream.seek(0)

    if ext == ".csv":
        return pd.read_csv(archivo, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(archivo)

    raise ValueError("Formato no soportado")

# =========================
# COLUMNAS
# =========================
@formato_bp.route("/columnas", methods=["POST"])
def columnas():
    archivo = request.files.get("archivo")
    df = leer_archivo(archivo)
    return jsonify(ok=True, columnas=df.columns.tolist())

# =========================
# DETECTAR FORMATO
# =========================
def detectar_formato(valores):
    patrones = Counter()

    for v in valores.dropna():
        s = str(v)[:10]
        if re.match(r"\d{4}-\d{2}-\d{2}", s):
            patrones["YMD"] += 1
        elif re.match(r"\d{2}/\d{2}/\d{4}", s):
            d, m, _ = s.split("/")
            patrones["DMY" if int(d) > 12 else "MDY"] += 1

    return patrones.most_common(1)[0][0] if patrones else None

# =========================
# PARSEAR
# =========================
def parsear(valor, formato):
    if pd.isna(valor):
        return None, None

    texto = str(valor)
    fecha_txt = texto[:10]

    formatos = {
        "DMY": "%d/%m/%Y",
        "MDY": "%m/%d/%Y",
        "YMD": "%Y-%m-%d"
    }

    try:
        dt = datetime.strptime(fecha_txt, formatos[formato])
        fecha = dt.strftime("%d/%m/%Y")
        hora = texto[11:16] if len(texto) >= 16 else None
        return fecha, hora
    except:
        return None, None

# =========================
# EJECUTAR
# =========================
@formato_bp.route("/ejecutar", methods=["POST"])
def ejecutar():
    archivo = request.files.get("archivo")
    columna = request.form.get("columna")

    df = leer_archivo(archivo)
    formato = detectar_formato(df[columna])

    if not formato:
        return jsonify(ok=False, error="No se pudo detectar formato")

    col_fecha = f"{columna}_fecha"
    col_hora = f"{columna}_hora"

    df[col_fecha], df[col_hora] = zip(
        *df[columna].apply(lambda x: parsear(x, formato))
    )

    token = str(uuid.uuid4())
    salida = os.path.join(TEMP_DIR, f"{token}.xlsx")
    df.to_excel(salida, index=False)

    preview = df[[col_fecha, col_hora]].head(10).to_dict("records")

    return jsonify(
        ok=True,
        formato=formato,
        columnas=[col_fecha, col_hora],
        preview=preview,
        token=token
    )

# =========================
# DESCARGAR
# =========================
@formato_bp.route("/descargar/<token>")
def descargar(token):
    ruta = os.path.join(TEMP_DIR, f"{token}.xlsx")
    return send_file(ruta, as_attachment=True, download_name="resultado_fecha_hora.xlsx")
