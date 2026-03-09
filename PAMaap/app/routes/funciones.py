from flask import render_template, redirect, url_for, session, request, send_file
import pandas as pd
import os
import re
from datetime import datetime
import csv
from collections import Counter
from io import BytesIO
import openpyxl

# =========================
# CONFIGURACIÓN DE RUTA BASE
# =========================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "archives")


# =========================
# CARPETA PRIVADA DEL USUARIO
# =========================

def get_user_folder():
    user_id = session["user"]["id"]
    fullname = session["user"]["fullname"]

    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', fullname).lower()
    folder_name = f"user_{user_id}_{safe_name}"

    user_folder = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(user_folder, exist_ok=True)

    return user_folder


# =========================
# FUNCIONES
# =========================

def funcion():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("funciones.html")


# =========================
# ANALISIS
# =========================

def F_analisis():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("F_analisis.html")


# =========================
# REPORTES (MOSTRAR ARCHIVOS)
# =========================

def F_reportes():
    if "user" not in session:
        return redirect(url_for("login"))

    user_folder = get_user_folder()
    archivos = []

    if os.path.exists(user_folder):
        for nombre in os.listdir(user_folder):
            ruta = os.path.join(user_folder, nombre)

            if os.path.isfile(ruta):
                archivos.append(nombre)

    return render_template("F_reportes.html", archivos=archivos)
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––---------------------------------------------------------------------------

def F_top5():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        archivo = request.form.get("archivo_seleccionado")

        if not archivo:
            return redirect(url_for("reportes"))

        user_folder = get_user_folder()
        ruta_completa = os.path.join(user_folder, archivo)

        if not os.path.exists(ruta_completa):
            return "Error: El archivo no existe."

        servidores = []
        incidentes = []
        detalle_incidentes = {}

        # ==============================
        # 1️⃣ Leer CSV dinámicamente
        # ==============================

        with open(ruta_completa, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]

            for fila in reader:

                mostrar_id = fila.get("Mostrar ID", "").strip()
                external_ticket = fila.get("External System Ticket", "").strip()
                resumen = fila.get("Resumen", "").strip()
                analista = fila.get("Analista gestionador", "").strip()
                estado = fila.get("Estado", "").strip()

                if not mostrar_id.upper().startswith("INC"):
                    continue

                if not external_ticket:
                    continue

                hostname = external_ticket.upper()

                servidores.append(hostname)

                incidentes.append({
                    "mostrar_id": mostrar_id,
                    "analista": analista,
                    "estado": estado,
                    "resumen": resumen,
                    "ticket": hostname
                })

                if hostname not in detalle_incidentes:
                    detalle_incidentes[hostname] = []

                detalle_incidentes[hostname].append({
                    "id": mostrar_id,
                    "resumen": resumen
                })

        # ==============================
        # 2️⃣ Top 5
        # ==============================

        contador = Counter(servidores)
        top5 = contador.most_common(5)

        # ==============================
        # 3️⃣ Cargar Inventarios
        # ==============================

        base_path = os.path.join(
            PROJECT_ROOT,
            "archives",
            "XLXS_IMPORT",
            "ALIMENTADORES"
        )

        infra_path = os.path.join(base_path, "INVENTARIO_INFRA_beta.xlsx")
        ad_path = os.path.join(base_path, "INVENTARIO_AD_beta.xlsx")

        def cargar_excel_seguro(path):

            if not os.path.exists(path):
                return pd.DataFrame()

            df = pd.read_excel(path)

            df.columns = df.columns.astype(str).str.strip().str.upper()

            if "NOMBRE SERVERS" in df.columns:
                df["NOMBRE SERVERS"] = (
                    df["NOMBRE SERVERS"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

            return df

        infra_df = cargar_excel_seguro(infra_path)
        ad_df = cargar_excel_seguro(ad_path)

        # ==============================
        # 4️⃣ Construcción resultado
        # ==============================

        resultado_final = []

        for servidor, cantidad in top5:

            doliente = "Otros"
            datos_servidor = {}

            if not infra_df.empty and "NOMBRE SERVERS" in infra_df.columns:
                match = infra_df[infra_df["NOMBRE SERVERS"] == servidor]

                if not match.empty:
                    doliente = "Microsoft Infra"
                    datos_servidor = match.iloc[0].to_dict()

            if doliente == "Otros" and not ad_df.empty and "NOMBRE SERVERS" in ad_df.columns:
                match = ad_df[ad_df["NOMBRE SERVERS"] == servidor]

                if not match.empty:
                    doliente = "Microsoft AD"
                    datos_servidor = match.iloc[0].to_dict()

            registro = {
                "servidor": servidor,
                "cantidad": cantidad,
                "doliente": doliente,
                "incidentes": detalle_incidentes.get(servidor, [])
            }

            for key, value in datos_servidor.items():
                if key != "NOMBRE SERVERS":
                    registro[key.lower()] = value

            resultado_final.append(registro)

        # ==============================
        # 5️⃣ Generar texto del análisis
        # ==============================

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")

        texto_analisis = f"""{fecha_hoy}

Se realiza análisis del TOP 5 de los servidores con más incidentes:

"""

        dolientes = {}

        for item in resultado_final:
            doliente = item["doliente"]

            if doliente not in dolientes:
                dolientes[doliente] = []

            dolientes[doliente].append(item)

        for doliente, servidores_lista in dolientes.items():

            texto_analisis += f"\nDoliente: {doliente} [\n"

            for idx, servidor in enumerate(servidores_lista, start=1):

                incidentes_lista = servidor.get("incidentes", [])

                incidentes_texto = ", ".join(
                    [f"{inc['id']} - {inc['resumen']}" for inc in incidentes_lista]
                )

                texto_analisis += (
                    f"\t{idx:02d}. {servidor['servidor']}: "
                    f"{servidor['cantidad']} casos ({incidentes_texto})\n"
                )

                texto_analisis += "\tNOTA:\n\n"

            texto_analisis += "]\n"

        return render_template(
            "F_reportes.html",
            archivos=os.listdir(user_folder),
            top5_detallado=resultado_final,
            incidentes=incidentes,
            texto_analisis=texto_analisis
        )

    return redirect(url_for("reportes"))