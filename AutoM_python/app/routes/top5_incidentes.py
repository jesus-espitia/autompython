import pandas as pd
from datetime import datetime, timedelta
import os
import re

def topDeInicidentes():
    try:
        print("📊 Ejecutando análisis Top 5 de incidentes...")
        print(" ⚠️ RECUERDA QUE ESTO SE EJECUTA DE VIERNES A VIERNES ⚠️ \n")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        csv_dir = os.path.join(project_root, "Ruta-CSV")
        txt_dir = os.path.join(project_root, "Ruta-TXT")
        excel_dir = os.path.join(project_root, "Excel", "ARCHIVOS_ALIMENTADORES_INFRA_AD")

        infra_file = os.path.join(excel_dir, "INVENTARIO_INFRA_beta.xlsx")
        ad_file = os.path.join(excel_dir, "INVENTARIO_AD_beta.xlsx")

        # ---------- CARGAR INVENTARIOS ----------
        def cargar_inventario(path):
            if not os.path.exists(path):
                return pd.DataFrame()
            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]

            # ELIMINAR FILAS SIN SERVIDOR
            df = df[df.iloc[:,0].notna()]

            # NORMALIZAR SERVIDOR
            df.iloc[:,0] = df.iloc[:,0].astype(str).str.upper().str.strip()
            return df

        infra_inv = cargar_inventario(infra_file)
        ad_inv = cargar_inventario(ad_file)

        # ---------- CARGAR INCIDENTES ----------
        archivos = [f for f in os.listdir(csv_dir) if f.endswith((".csv", ".xlsx", ".xls"))]
        if not archivos:
            print("❌ No hay archivos de incidentes.")
            return

        df = None
        for archivo in archivos:
            try:
                path = os.path.join(csv_dir, archivo)
                df = pd.read_csv(path) if path.endswith(".csv") else pd.read_excel(path)
                break
            except:
                continue
        if df is None:
            print("❌ No hay archivos válidos.")
            return

        df.columns = [re.sub(r"\s+", " ", c).strip().lower() for c in df.columns]

        col_id, col_ticket, col_resumen = "mostrar id", "external system ticket", "resumen"
        df_inc = df[df[col_id].astype(str).str.startswith("INC")]

        # ELIMINAR INCIDENTES SIN SERVIDOR
        df_inc = df_inc[df_inc[col_ticket].notna()]

        # NORMALIZAR SERVIDOR INCIDENTE
        df_inc[col_ticket] = df_inc[col_ticket].astype(str).str.upper().str.strip()

        top5 = df_inc[col_ticket].value_counts().head(5)

        # ---------- CLASIFICAR ----------
        resultado = {"Microsoft Infra": [], "Microsoft AD": [], "OTROS": []}

        for hostname, count in top5.items():
            detalles = df_inc[df_inc[col_ticket] == hostname][col_resumen].dropna().tolist()
            detalles_texto = ", ".join(detalles)

            tipo = "SIN TIPO"

            if hostname in infra_inv.iloc[:,0].values:
                fila = infra_inv[infra_inv.iloc[:,0] == hostname].iloc[0]
                tipo = fila["tipo_server"]
                resultado["Microsoft Infra"].append((hostname, tipo, count, detalles_texto))

            elif hostname in ad_inv.iloc[:,0].values:
                fila = ad_inv[ad_inv.iloc[:,0] == hostname].iloc[0]
                tipo = fila["tipo_server"]
                resultado["Microsoft AD"].append((hostname, tipo, count, detalles_texto))
            else:
                resultado["OTROS"].append((hostname, tipo, count, detalles_texto))

        # ---------- GENERAR REPORTE ----------
        fecha_actual = datetime.now()
        fecha_inicio = fecha_actual - timedelta(days=7)

        rep = []
        rep.append(f"{fecha_actual.strftime('%d/%m/%Y')}\n")
        rep.append(f"Se realiza análisis del TOP 5 de los servidores con más incidentes entre "
                    f"{fecha_inicio.strftime('%d/%m/%Y')} y {fecha_actual.strftime('%d/%m/%Y')}:\n")

        for doliente, servers in resultado.items():
            if not servers:
                continue
            rep.append(f"\nDoliente: {doliente} [")
            for i, (h,t,c,d) in enumerate(servers,1):
                rep.append(f"\t{i:02d}. {h} ({t}): {c} casos ({d})")
                rep.append("\tNOTA:\n")
            rep.append("]")

        os.makedirs(txt_dir, exist_ok=True)

        fecha_archivo = datetime.now().strftime("%d-%m-%Y")
        out = os.path.join(txt_dir, f"Reporte_Incidentes_{fecha_archivo}.txt")

        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(rep))

        print(f"📝 Reporte generado correctamente en: {out}\n")

    except Exception as e:
        print(f"❌ Error ejecutando topDeInicidentes: {e}")
