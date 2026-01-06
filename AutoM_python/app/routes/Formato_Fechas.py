import pandas as pd
import os
import re
from dateutil import parser

def separar_fecha_hora_reporte_scaneo():
    try:
        print("🧩 Separando fecha y hora desde 'Reporte Scaneo'...\n")

        ruta_archivo = r"C:\Users\carlos.bedoya\Documents\Documentacion\Equipo Infra\Scripts Python\Top_5_INC\PoweShell EXP\Excel\WSUS.xlsx"

        if not os.path.exists(ruta_archivo):
            print("❌ El archivo no existe.")
            return

        # Cargar archivo
        if ruta_archivo.endswith(".csv"):
            df = pd.read_csv(ruta_archivo)
        else:
            df = pd.read_excel(ruta_archivo)

        columnas_originales = df.columns.tolist()

        # Normalizar nombres de columnas
        df.columns = [
            re.sub(r"\s+", " ", col).strip().lower()
            for col in df.columns
        ]

        col_origen = "reporte scaneo"

        if col_origen not in df.columns:
            print("❌ No se encontró la columna 'Reporte Scaneo'")
            print("📌 Columnas encontradas:", columnas_originales)
            return

        # Crear nuevas columnas
        df["fecha scaneo"] = ""
        df["hora scaneo"] = ""

        def extraer_fecha_hora(valor):
            if pd.isna(valor):
                return "", ""

            texto = str(valor).strip()

            try:
                dt = parser.parse(texto, dayfirst=True, fuzzy=True)

                tiene_fecha = bool(
                    re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", texto)
                )

                fecha = dt.strftime("%d/%m/%Y") if tiene_fecha else ""
                hora  = dt.strftime("%H:%M")

                return fecha, hora

            except Exception:
                return "", ""

        # Aplicar extracción
        df[["fecha scaneo", "hora scaneo"]] = df[col_origen].apply(
            lambda x: pd.Series(extraer_fecha_hora(x))
        )

        # Guardar sobrescribiendo
        if ruta_archivo.endswith(".csv"):
            df.to_csv(ruta_archivo, index=False)
        else:
            df.to_excel(ruta_archivo, index=False)

        print("✅ Columnas 'Fecha Scaneo' y 'Hora Scaneo' creadas correctamente.\n")

    except Exception as e:
        print(f"❌ Error ejecutando separar_fecha_hora_reporte_scaneo: {e}")

 