import pandas as pd
from datetime import datetime, timedelta
import os
import re

def topDeInicidentes():
    try:
        print("📊 Ejecutando análisis Top 5 de incidentes...\n")

        csv_dir = r"C:\Users\jesuesgu\Documents\PoweShell EXP\Ruta-CSV"
        txt_dir = r"C:\Users\jesuesgu\Documents\PoweShell EXP\Ruta-TXT"

        # Buscar archivos CSV y Excel
        archivos = [f for f in os.listdir(csv_dir) if f.endswith((".csv", ".xlsx", ".xls"))]

        if not archivos:
            print("❌ No se encontró ningún archivo CSV ni Excel en la carpeta especificada.")
            return

        df = None

        # Intentar cargar archivos hasta encontrar uno válido
        for archivo in archivos:
            archivo_path = os.path.join(csv_dir, archivo)
            try:
                if archivo_path.endswith(".csv"):
                    df = pd.read_csv(archivo_path)
                else:
                    df = pd.read_excel(archivo_path)

                print(f"📌 Archivo cargado: {archivo}")
                break
            except Exception:
                print(f"⚠️ Archivo inválido o corrupto ignorado: {archivo}")
                continue

        if df is None:
            print("❌ Ningún archivo válido para procesar.")
            return

        # 🔥 Normalizar nombres de columnas para evitar errores
        columnas_originales = df.columns.tolist()
        df.columns = [re.sub(r"\s+", " ", col).strip().lower() for col in df.columns]

        # Intentar localizar la columna Mostrar ID ya normalizada
        if "mostrar id" not in df.columns:
            print("❌ No se encontró la columna 'Mostrar ID' en el archivo (nombre puede estar cambiado).")
            print("📌 Columnas encontradas:", columnas_originales)
            return

        col_id = "mostrar id"
        col_ticket = "external system ticket".lower()
        col_resumen = "resumen".lower()

        # Validar las demás columnas
        if col_ticket not in df.columns or col_resumen not in df.columns:
            print("❌ Faltan columnas obligatorias en el archivo.")
            print("📌 Columnas encontradas:", columnas_originales)
            return

        # Obtener DataFrame normalizado con nombres corregidos
        df_inc = df[df[col_id].astype(str).str.startswith("INC")]

        conteo = df_inc[col_ticket].value_counts().head(5)

        fecha_actual = datetime.now()
        fecha_inicio = fecha_actual - timedelta(days=7)

        reporte = []
        reporte.append(f"{fecha_actual.strftime('%d/%m/%Y')}\n")
        reporte.append(
            f"Se realiza análisis del TOP 5 de los servidores con más incidentes entre "
            f"{fecha_inicio.strftime('%d/%m/%Y')} y {fecha_actual.strftime('%d/%m/%Y')}:\n\n"
        )

        for i, (hostname, count) in enumerate(conteo.items(), start=1):
            detalles = df_inc[df_inc[col_ticket] == hostname][col_resumen].dropna().tolist()
            detalles_texto = ", ".join(detalles)
            reporte.append(f"{i:02d}. {hostname}: {count} casos ({detalles_texto})")
            reporte.append("NOTA:\n")

        os.makedirs(txt_dir, exist_ok=True)
        ruta_salida = os.path.join(txt_dir, "Reporte_Incidentes.txt")
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write("\n".join(reporte))

        print(f"📝 Reporte generado correctamente en: {ruta_salida}\n")

    except Exception as e:
        print(f"❌ Error ejecutando topDeInicidentes: {e}")
