from flask import render_template, redirect, url_for, session, request
import pandas as pd
import os
import re

# =========================
# CONFIGURACIÓN
# =========================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "archives")

ALIMENTADORES_PATH = os.path.join(
    UPLOAD_FOLDER,
    "XLXS_IMPORT",
    "ALIMENTADORES"
)

INFRA_FILE = os.path.join(ALIMENTADORES_PATH, "INVENTARIO_INFRA_beta.xlsx")
AD_FILE = os.path.join(ALIMENTADORES_PATH, "INVENTARIO_AD_beta.xlsx")


# =========================
# CARPETA USUARIO
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
# NORMALIZAR HOSTNAME
# =========================

def limpiar_hostname(host):

    if pd.isna(host):
        return None

    host = str(host).strip().lower()

    if "@" in host:
        host = host.split("@")[0]

    if "." in host:
        host = host.split(".")[0]

    return host


# =========================
# CARGAR ALIMENTADORES
# =========================

def cargar_alimentadores():

    infra_hosts = set()
    ad_hosts = set()

    if os.path.exists(INFRA_FILE):
        df = pd.read_excel(INFRA_FILE)

        if "NOMBRE SERVERS" in df.columns:
            for h in df["NOMBRE SERVERS"]:
                host = limpiar_hostname(h)
                if host:
                    infra_hosts.add(host)

    if os.path.exists(AD_FILE):
        df = pd.read_excel(AD_FILE)

        if "NOMBRE SERVERS" in df.columns:
            for h in df["NOMBRE SERVERS"]:
                host = limpiar_hostname(h)
                if host:
                    ad_hosts.add(host)

    return infra_hosts, ad_hosts


# =========================
# LEER ARCHIVO USUARIO
# =========================

def leer_archivo(path):

    if path.endswith(".csv"):
        return pd.read_csv(path)

    if path.endswith(".xlsx"):
        return pd.read_excel(path)

    return None


# =========================
# MODULO PRINCIPAL
# =========================

def F_comparacionArchivo():

    if "user" not in session:
        return redirect(url_for("login"))

    user_folder = get_user_folder()

    archivos = [
        f for f in os.listdir(user_folder)
        if f.endswith(".csv") or f.endswith(".xlsx")
    ]

    columnas = []
    resultados = None

    archivo_seleccionado = None
    columna_seleccionada = None

    # =========================
    # PASO 1: detectar columnas
    # =========================

    if request.method == "POST":

        archivo_seleccionado = request.form.get("archivo")

        if archivo_seleccionado:

            path = os.path.join(user_folder, archivo_seleccionado)

            df = leer_archivo(path)

            if df is not None:
                columnas = list(df.columns)

        columna_seleccionada = request.form.get("columna")

        # =========================
        # PASO 2: comparar
        # =========================

        if columna_seleccionada:

            df = leer_archivo(path)

            servidores = set()

            for s in df[columna_seleccionada]:

                host = limpiar_hostname(s)

                if host:
                    servidores.add(host)

            infra_hosts, ad_hosts = cargar_alimentadores()

            infra = []
            ad = []
            otros = []

            for s in servidores:

                if s in infra_hosts:
                    infra.append(s)

                elif s in ad_hosts:
                    ad.append(s)

                else:
                    otros.append(s)

            resultados = {
                "infra": sorted(infra),
                "ad": sorted(ad),
                "otros": sorted(otros)
            }

    return render_template(
        "F_comparacionArchivos.html",
        archivos=archivos,
        columnas=columnas,
        resultados=resultados,
        archivo_seleccionado=archivo_seleccionado
    )