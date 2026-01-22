import os
import pandas as pd
from flask import Blueprint, request, jsonify
from datetime import datetime

comparar_bp = Blueprint("comparar", __name__)

# =========================
# RUTAS RELATIVAS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ARCHIVOS_GUARDADOS = os.path.join(BASE_DIR, "ArchivosGuardados")
EXCEL_DIR = os.path.join(BASE_DIR, "static", "ARCHIVOS_ALIMENTADORES_INFRA_AD")

os.makedirs(ARCHIVOS_GUARDADOS, exist_ok=True)

# =========================
# NORMALIZADOR
# =========================
def normalizar(v):
    if pd.isna(v):
        return None
    return str(v).strip().upper().split(".")[0]

# =========================
# CARGAR INVENTARIO
# =========================
def cargar_inventario(nombre):
    path = os.path.join(EXCEL_DIR, nombre)
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_excel(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df.iloc[:, 0] = df.iloc[:, 0].apply(normalizar)
    return df

# =========================
# RECOLECTAR COLUMNAS
# =========================
@comparar_bp.route("/comparar/columnas", methods=["POST"])
def recolectar_columnas():
    archivo = request.files.get("archivo")
    if not archivo:
        return jsonify(ok=False, error="No se recibió archivo")

    ext = os.path.splitext(archivo.filename)[1].lower()
    if ext not in [".csv", ".xlsx", ".xls"]:
        return jsonify(ok=False, error="Formato no soportado")

    df = pd.read_csv(archivo) if ext == ".csv" else pd.read_excel(archivo)

    return jsonify(
        ok=True,
        archivo=archivo.filename,
        columnas=df.columns.tolist()
    )

# =========================
# EJECUTAR COMPARACIÓN
# =========================
@comparar_bp.route("/comparar/ejecutar", methods=["POST"])
def ejecutar():
    archivo = request.files.get("archivo")
    columna = request.form.get("columna")
    guardar = request.form.get("guardar") == "true"

    if not archivo or not columna:
        return jsonify(ok=False, error="Datos incompletos")

    ext = os.path.splitext(archivo.filename)[1].lower()
    df_rep = pd.read_csv(archivo) if ext == ".csv" else pd.read_excel(archivo)

    servidores = (
        df_rep[columna]
        .apply(normalizar)
        .dropna()
        .unique()
    )

    infra = cargar_inventario("INVENTARIO_INFRA_beta.xlsx")
    ad = cargar_inventario("INVENTARIO_AD_beta.xlsx")

    resultado = {
        "Microsoft Infra": [],
        "Microsoft AD": [],
        "OTROS": []
    }

    for srv in servidores:
        if srv in infra.iloc[:, 0].values:
            fila = infra[infra.iloc[:, 0] == srv].iloc[0]
            tipo = fila.get("tipo_server", "SIN TIPO")
            resultado["Microsoft Infra"].append((srv, tipo))

        elif srv in ad.iloc[:, 0].values:
            fila = ad[ad.iloc[:, 0] == srv].iloc[0]
            tipo = fila.get("tipo_server", "SIN TIPO")
            resultado["Microsoft AD"].append((srv, tipo))

        else:
            resultado["OTROS"].append((srv, "SIN TIPO"))

    # =========================
    # FORMATO FINAL
    # =========================
    fecha = datetime.now().strftime("%d-%m-%Y")

    rep = [
        fecha,
        "",
        f"Reporte analizado: {archivo.filename}",
        f"Columna comparada: {columna}",
        ""
    ]

    for doliente, items in resultado.items():
        if not items:
            continue

        rep.append(f"\nDoliente: {doliente} [")
        for i, (srv, tipo) in enumerate(items, 1):
            rep.append(f"\t{i:02d}. {srv} ({tipo})")
        rep.append("\n]")

    texto_final = "\n".join(rep)

    # =========================
    # GUARDADO OPCIONAL DEL ARCHIVO ORIGINAL
    # =========================
    archivo_guardado = None
    if guardar:
        ruta = os.path.join(ARCHIVOS_GUARDADOS, archivo.filename)
        archivo.stream.seek(0)
        archivo.save(ruta)
        archivo_guardado = archivo.filename

    return jsonify(
        ok=True,
        resultado=texto_final,
        archivo_guardado=archivo_guardado
    )
