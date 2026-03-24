from flask import render_template, redirect, url_for, session, request
import os
import json

# =========================
# RUTA BASE DEL PROYECTO
# =========================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_FOLDER = os.path.join(PROJECT_ROOT, "archives", "public")

# archivo donde guardamos dueños
META_FILE = os.path.join(PUBLIC_FOLDER, "owners.json")


# =========================
# ASEGURAR CARPETA + JSON
# =========================
def get_public_folder():
    os.makedirs(PUBLIC_FOLDER, exist_ok=True)

    if not os.path.exists(META_FILE):
        with open(META_FILE, "w") as f:
            json.dump({}, f)

    return PUBLIC_FOLDER


# =========================
# LEER / GUARDAR JSON
# =========================
def cargar_meta():
    if not os.path.exists(META_FILE):
        return {}

    with open(META_FILE, "r") as f:
        return json.load(f)


def guardar_meta(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# CREAR MES
# =========================
def crear_mes(nombre_mes):
    ruta_base = get_public_folder()
    ruta_mes = os.path.join(ruta_base, nombre_mes)

    if not os.path.exists(ruta_mes):
        os.makedirs(os.path.join(ruta_mes, "CPU y Memoria"))
        os.makedirs(os.path.join(ruta_mes, "Disco"))


# =========================
# LISTAR MESES
# =========================
def listar_meses():
    ruta_base = get_public_folder()

    if not os.path.exists(ruta_base):
        return []

    meses = [
        carpeta for carpeta in os.listdir(ruta_base)
        if os.path.isdir(os.path.join(ruta_base, carpeta))
    ]

    print("MESES DETECTADOS:", meses)

    return meses


# =========================
# LISTAR ARCHIVOS COMPLETOS
# =========================
def listar_publicos():
    ruta_base = get_public_folder()
    estructura = []
    meta = cargar_meta()

    for mes in listar_meses():
        ruta_mes = os.path.join(ruta_base, mes)

        data = {
            "mes": mes,
            "cpu": [],
            "disco": []
        }

        ruta_cpu = os.path.join(ruta_mes, "CPU y Memoria")
        ruta_disco = os.path.join(ruta_mes, "Disco")

        if os.path.exists(ruta_cpu):
            for archivo in os.listdir(ruta_cpu):
                owner = meta.get(f"{mes}/CPU y Memoria/{archivo}", "Desconocido")

                data["cpu"].append({
                    "nombre": archivo,
                    "owner": owner
                })

        if os.path.exists(ruta_disco):
            for archivo in os.listdir(ruta_disco):
                owner = meta.get(f"{mes}/Disco/{archivo}", "Desconocido")

                data["disco"].append({
                    "nombre": archivo,
                    "owner": owner
                })

        estructura.append(data)

    return estructura


# =========================
# SUBIR ARCHIVO
# =========================
def subir_archivo(archivo, mes, subcarpeta):
    if not archivo or archivo.filename == "":
        return

    if not archivo.filename.endswith(".xlsx"):
        return

    ruta = os.path.join(get_public_folder(), mes, subcarpeta)

    if os.path.exists(ruta):
        ruta_archivo = os.path.join(ruta, archivo.filename)
        archivo.save(ruta_archivo)

        # guardar dueño
        meta = cargar_meta()
        key = f"{mes}/{subcarpeta}/{archivo.filename}"
        meta[key] = session["user"]["fullname"]
        guardar_meta(meta)


# =========================
# ELIMINAR (solo dueño)
# =========================
def eliminar_archivo(mes, subcarpeta, nombre_archivo):
    ruta = os.path.join(get_public_folder(), mes, subcarpeta, nombre_archivo)

    meta = cargar_meta()
    key = f"{mes}/{subcarpeta}/{nombre_archivo}"

    owner = meta.get(key)

    if owner != session["user"]["fullname"]:
        print("NO TIENE PERMISO")
        return

    if os.path.exists(ruta):
        os.remove(ruta)
        meta.pop(key, None)
        guardar_meta(meta)


# =========================
# CONTROLADOR PRINCIPAL
# =========================
def documentosPublicos():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        accion = request.form.get("accion")
        mes = request.form.get("mes")
        subcarpeta = request.form.get("subcarpeta")
        archivo = request.files.get("archivo")
        nombre_archivo = request.form.get("archivo")

        print("POST ->", accion, mes, subcarpeta)

        # 🔥 ELIMINAR
        if accion == "eliminar":
            eliminar_archivo(mes, subcarpeta, nombre_archivo)

        # CREAR MES
        elif mes and not archivo:
            crear_mes(mes)

        # SUBIR ARCHIVO
        elif mes and subcarpeta and archivo:
            subir_archivo(archivo, mes, subcarpeta)

        return redirect(url_for("documentosPublicosVisualizar"))

    meses = listar_meses()
    publicos = listar_publicos()

    return render_template(
        "documentosPublicos.html",
        meses=meses,
        publicos=publicos
    )