import os
import re
import pandas as pd
from datetime import datetime

def TopINCMensuales():
    try:
        print("📊 Generador de Reporte Mensual de Incidentes\n")

        # ---------- RUTAS ----------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        txt_dir = os.path.join(project_root, "Ruta-TXT", "ReportePasado")
        excel_dir = os.path.join(project_root, "Excel")
        excel_inv = os.path.join(project_root, "Excel", "ARCHIVOS_ALIMENTADORES_INFRA_AD")

        infra_file = os.path.join(excel_inv, "INVENTARIO_INFRA_beta.xlsx")
        ad_file = os.path.join(excel_inv, "INVENTARIO_AD_beta.xlsx")

        # ---------- INPUT MES / AÑO ----------
        mes = input("📅 Ingresa el mes (1-12): ").strip()
        anio = input("📅 Ingresa el año (YYYY): ").strip()

        if not mes.isdigit() or not (1 <= int(mes) <= 12):
            print("❌ Mes inválido.")
            return

        if not anio.isdigit() or len(anio) != 4:
            print("❌ Año inválido.")
            return

        mes = mes.zfill(2)

        print(f"\n🔍 Procesando reportes de {mes}-{anio}\n")

        # ---------- CARGAR INVENTARIOS ----------
        def cargar_inv(path):
            if not os.path.exists(path):
                return pd.DataFrame()

            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]
            df = df[df.iloc[:, 0].notna()]
            df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.upper().str.strip()
            return df

        infra_inv = cargar_inv(infra_file)
        ad_inv = cargar_inv(ad_file)

        # ---------- DETECTAR COLUMNA UBICACIÓN ----------
        def detectar_columna(df):
            for col in df.columns:
                if "ubicacion" in col:
                    return col
            return None

        col_ubi_infra = detectar_columna(infra_inv)
        col_ubi_ad = detectar_columna(ad_inv)

        # ---------- FILTRAR TXT ----------
        archivos = [
            f for f in os.listdir(txt_dir)
            if f.startswith("Reporte_Incidentes_")
            and f.endswith(".txt")
            and f[-8:-4] == anio
            and f[-11:-9] == mes
        ]

        if not archivos:
            print("❌ No se encontraron reportes para ese mes/año.")
            return

        registros = []

        # ---------- LEER TXT ----------
        for archivo in archivos:
            path = os.path.join(txt_dir, archivo)
            fecha_txt = archivo.replace("Reporte_Incidentes_", "").replace(".txt", "")
            fecha_reporte = datetime.strptime(fecha_txt, "%d-%m-%Y").date()

            with open(path, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            doliente = ""

            for linea in lineas:
                linea = linea.strip()

                if linea.startswith("Doliente:"):
                    doliente = linea.replace("Doliente:", "").replace("[", "").strip()

                match = re.match(r"\d+\.\s+([A-Z0-9_]+)", linea)
                if match:
                    servidor = match.group(1)

                    tipo = ""
                    casos = 0
                    detalles = ""

                    tipo_match = re.search(r"\(([^)]*)\)", linea)
                    if tipo_match:
                        tipo = tipo_match.group(1)

                    casos_match = re.search(r":\s*(\d+)\s+casos", linea)
                    if casos_match:
                        casos = int(casos_match.group(1))

                    detalle_match = re.findall(r"\((.*?)\)", linea)
                    if len(detalle_match) > 1:
                        raw = detalle_match[1]
                        raw = re.sub(r"Solarwinds\s*\d+\s*-\s*", "", raw)
                        detalles = ", ".join(sorted(set(x.strip() for x in raw.split(",") if x.strip())))

                    registros.append({
                        "FechaReporte": fecha_reporte,
                        "Año": int(anio),
                        "Mes": mes,
                        "Doliente": doliente,
                        "Servidor": servidor,
                        "Tipo": tipo,
                        "Casos": casos,
                        "Detalles": detalles
                    })

        df = pd.DataFrame(registros)

        # ---------- ACUMULAR CASOS ----------
        df = df.groupby(
            ["Año", "Mes", "Doliente", "Servidor", "Tipo"],
            as_index=False
        ).agg({
            "Casos": "sum",
            "Detalles": lambda x: ", ".join(sorted(set(filter(None, x))))
        })

        # ---------- UBICACIÓN SEGURA ----------
        def obtener_ubicacion(server):
            if not infra_inv.empty and server in infra_inv.iloc[:, 0].values and col_ubi_infra:
                val = infra_inv.loc[infra_inv.iloc[:, 0] == server, col_ubi_infra]
                return val.values[0] if not val.empty else ""

            if not ad_inv.empty and server in ad_inv.iloc[:, 0].values and col_ubi_ad:
                val = ad_inv.loc[ad_inv.iloc[:, 0] == server, col_ubi_ad]
                return val.values[0] if not val.empty else ""

            return ""

        df["Ubicacion"] = df["Servidor"].apply(obtener_ubicacion)

        # ---------- EXPORTAR EXCEL ----------
        os.makedirs(excel_dir, exist_ok=True)

        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        salida = os.path.join(
            excel_dir,
            f"Reporte_Mensual_Incidentes_{fecha_hoy}.xlsx"
        )

        df.to_excel(salida, index=False)

        print("📈 Reporte mensual generado correctamente:")
        print(salida)

    except Exception as e:
        print(f"❌ Error en TopINC_Mensuales: {e}")
