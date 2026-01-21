import pandas as pd
import os
import re
from datetime import datetime

def TopINCMensuales():
    try:
        print("📊 Ejecutando análisis TOP mensual de incidentes...\n")

        # ---------- PEDIR MES Y AÑO ----------
        mes = int(input("📅 Ingresa el MES (1-12): "))
        anio = int(input("📅 Ingresa el AÑO (YYYY): "))

        # ---------- RUTAS RELATIVAS ----------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        csv_dir = os.path.join(project_root, "Ruta-CSV", "CSVPasado")
        excel_out_dir = os.path.join(project_root, "Excel")
        inventarios_dir = os.path.join(project_root, "Excel", "ARCHIVOS_ALIMENTADORES_INFRA_AD")

        infra_file = os.path.join(inventarios_dir, "INVENTARIO_INFRA_beta.xlsx")
        ad_file = os.path.join(inventarios_dir, "INVENTARIO_AD_beta.xlsx")

        # ---------- INVENTARIOS ----------
        def cargar_inventario(path):
            if not os.path.exists(path):
                return pd.DataFrame()
            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]
            df = df[df.iloc[:, 0].notna()]
            df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.upper().str.strip()
            return df

        infra_inv = cargar_inventario(infra_file)
        ad_inv = cargar_inventario(ad_file)

        # ---------- COLUMNAS ----------
        col_id = "mostrar id"
        col_ticket = "external system ticket"
        col_resumen = "resumen"

        acumulado = []

        archivos = sorted([f for f in os.listdir(csv_dir) if f.endswith(".csv")])

        if not archivos:
            print("❌ No hay CSV en CSVPasado")
            return

        # ---------- RECORRER CSV ----------
        for archivo in archivos:
            match = re.match(r"(\d{4})-(\d{2})-(\d{2})", archivo)
            if not match:
                continue

            file_year = int(match.group(1))
            file_month = int(match.group(2))
            file_date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

            if file_year != anio or file_month != mes:
                continue

            print(f"📂 Procesando: {archivo}")

            path = os.path.join(csv_dir, archivo)
            try:
                df = pd.read_csv(path, encoding="utf-8", low_memory=False)
            except:
                continue

            df.columns = [re.sub(r"\s+", " ", c).strip().lower() for c in df.columns]

            if not all(c in df.columns for c in [col_id, col_ticket]):
                continue

            df = df[df[col_id].astype(str).str.startswith("INC")]
            df = df[df[col_ticket].notna()]

            df[col_ticket] = df[col_ticket].astype(str).str.upper().str.strip()
            df["fecha_reporte"] = file_date

            acumulado.append(df[[col_ticket, col_resumen, "fecha_reporte"]])

        if not acumulado:
            print("❌ No hay datos para ese mes/año")
            return

        df_final = pd.concat(acumulado, ignore_index=True)

        # ---------- FUNCIÓN LIMPIAR RESUMEN ----------
        def resumir_eventos(lista_resumen):
            patrones = [
                "server down",
                "high memory",
                "high cpu",
                "disk",
                "unreachable",
                "not responding",
                "service down"
            ]

            encontrados = set()

            for r in lista_resumen:
                if not isinstance(r, str):
                    continue

                texto = r.lower()
                texto = re.sub(r"solarwinds.*?-", "", texto)
                texto = re.sub(r"\d+", "", texto)

                for p in patrones:
                    if p in texto:
                        encontrados.add(p.title())

            if not encontrados:
                return "Evento recurrente"

            return " | ".join(sorted(encontrados))

        # ---------- AGRUPAR ----------
        filas = []

        for hostname, grupo in df_final.groupby(col_ticket):
            casos = len(grupo)
            fecha_reporte = grupo["fecha_reporte"].iloc[0]

            detalle = resumir_eventos(grupo[col_resumen].dropna().tolist())

            doliente = "OTROS"
            tipo = ""
            ubicacion = ""

            if not infra_inv.empty and hostname in infra_inv.iloc[:, 0].values:
                fila = infra_inv[infra_inv.iloc[:, 0] == hostname].iloc[0]
                doliente = "Microsoft Infra"
                tipo = fila.get("tipo_server", "")
                ubicacion = fila.get("ubicacion", "")

            elif not ad_inv.empty and hostname in ad_inv.iloc[:, 0].values:
                fila = ad_inv[ad_inv.iloc[:, 0] == hostname].iloc[0]
                doliente = "Microsoft AD"
                tipo = fila.get("tipo_server", "")
                ubicacion = fila.get("ubicacion", "")

            filas.append([
                fecha_reporte,
                doliente,
                hostname,
                tipo,
                casos,
                detalle,
                ubicacion
            ])

        df_reporte = pd.DataFrame(
            filas,
            columns=[
                "Fecha reporte",
                "Doliente",
                "Servidor",
                "Tipo",
                "Cantidad Incidentes",
                "Detalle",
                "Ubicación"
            ]
        )

        df_reporte.sort_values(
            by=["Doliente", "Cantidad Incidentes"],
            ascending=[True, False],
            inplace=True
        )

        os.makedirs(excel_out_dir, exist_ok=True)

        out_file = os.path.join(
            excel_out_dir,
            f"TOP_INCIDENTES_{anio}_{mes:02d}.xlsx"
        )

        df_reporte.to_excel(out_file, index=False)

        print(f"\n✅ Reporte mensual generado correctamente:")
        print(f"📄 {out_file}\n")

    except Exception as e:
        print(f"❌ Error ejecutando TopINCMensuales: {e}")
