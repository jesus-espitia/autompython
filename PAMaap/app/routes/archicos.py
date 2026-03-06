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

# =========================================================================================================================

def F_archivoVisualizar():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("F_archivoVisualizar.html")