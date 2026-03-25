from flask import render_template, redirect, url_for, session, request, send_file
import pandas as pd
import os
import zipfile
from io import BytesIO

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_PUBLIC = os.path.join(PROJECT_ROOT, "archives", "public")


# =========================
# 🔍 BUSCAR CABECERA
# =========================
def buscar_header(ruta_excel, palabra_clave):
    df = pd.read_excel(ruta_excel, header=None)

    for i, row in df.iterrows():
        if palabra_clave in row.values:
            return i
    return None


# =========================
# 🧠 DETERMINAR DOLIENTE
# =========================
def obtener_doliente(nombre):
    nombre = nombre.upper()

    if "AD-DC" in nombre:
        return "AD DS"
    elif "MIEMBROS" in nombre:
        return "INFRA"
    elif "APPWEB" in nombre:
        return "APPWEB"
    return "DESCONOCIDO"


# =========================
# 📊 PROCESAR CARPETA
# =========================
def procesar_carpeta(ruta_carpeta, tipo):
    dfs = []

    for archivo in os.listdir(ruta_carpeta):
        if not archivo.endswith(".xlsx"):
            continue

        ruta = os.path.join(ruta_carpeta, archivo)

        # Definir palabra clave según tipo
        palabra = "Node" if tipo == "cpu" else "Date"

        header_row = buscar_header(ruta, palabra)

        if header_row is None:
            continue

        df = pd.read_excel(ruta, header=header_row)

        # Limpiar columnas vacías
        df = df.loc[:, ~df.columns.isna()]

        # Agregar Doliente
        df["Doliente"] = obtener_doliente(archivo)

        dfs.append(df)

    if dfs:
        return pd.concat(dfs, ignore_index=True)

    return pd.DataFrame()


# =========================
# 📦 GENERAR ZIP
# =========================
def generar_zip(df_cpu, df_disco, mes):
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as z:
        # Crear Excel CPU
        cpu_bytes = BytesIO()
        df_cpu.to_excel(cpu_bytes, index=False)
        z.writestr("CPU_Memoria_Unificado.xlsx", cpu_bytes.getvalue())

        # Crear Excel Disco
        disco_bytes = BytesIO()
        df_disco.to_excel(disco_bytes, index=False)
        z.writestr("Disco_Unificado.xlsx", disco_bytes.getvalue())

    buffer.seek(0)
    return buffer


# =========================
# 🚀 FUNCIÓN PRINCIPAL
# =========================
def F_discoMemoriaCpu():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        mes = request.form.get("mes")

        ruta_mes = os.path.join(BASE_PUBLIC, mes)
        ruta_cpu = os.path.join(ruta_mes, "CPU y Memoria")
        ruta_disco = os.path.join(ruta_mes, "Disco")

        df_cpu = procesar_carpeta(ruta_cpu, "cpu")
        df_disco = procesar_carpeta(ruta_disco, "disco")

        zip_buffer = generar_zip(df_cpu, df_disco, mes)

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{mes}_unificado.zip",
            mimetype="application/zip"
        )

    # GET → listar meses disponibles
    meses = [
        carpeta for carpeta in os.listdir(BASE_PUBLIC)
        if os.path.isdir(os.path.join(BASE_PUBLIC, carpeta))
    ]

    return render_template("F_discoMemoriaCpu.html", meses=meses)