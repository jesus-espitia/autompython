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


def F_discoMemoriaCpu():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("F_discoMemoriaCpu.html")