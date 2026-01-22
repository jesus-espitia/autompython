import pandas as pd
from datetime import datetime, timedelta
import os
import re

def topDeInicidentes(csv_path):
    try:
        base_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(base_dir, ".."))

        static_dir = os.path.join(project_root, "static")
        excel_dir = os.path.join(static_dir, "ARCHIVOS_ALIMENTADORES_INFRA_AD")

        infra_file = os.path.join(excel_dir, "INVENTARIO_INFRA_beta.xlsx")
        ad_file = os.path.join(excel_dir, "INVENTARIO_AD_beta.xlsx")

        # ---------- CARGAR INVENTARIOS ----------
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

        # ---------- CARGAR INCIDENTES ----------
        if csv_path.endswith(".csv"):
            df = pd.read_csv(csv_path)
        else:
            df = pd.read_excel(csv_path)

        df.columns = [re.sub(r"\s+", " ", c).strip().lower() for c in df.columns]

        col_id = "mostrar id"
        col_ticket = "external system ticket"
        col_resumen = "resumen"

        df_inc = df[df[col_id].astype(str).str.startswith("INC")]
        df_inc = df_inc[df[col_ticket].notna()]
        df_inc[col_ticket] = df_inc[col_ticket].astype(str).str.upper().str.strip()

        # ---------- TOP 5 ----------
        top5 = df_inc[col_ticket].value_counts().head(5)

        resultado = {
            "Microsoft Infra": [],
            "Microsoft AD": [],
            "OTROS": []
        }

        for hostname, count in top5.items():
            detalles = df_inc[df_inc[col_ticket] == hostname][col_resumen].dropna().tolist()
            detalles_texto = ", ".join(detalles)

            if hostname in infra_inv.iloc[:, 0].values:
                fila = infra_inv[infra_inv.iloc[:, 0] == hostname].iloc[0]
                resultado["Microsoft Infra"].append(
                    (hostname, fila.get("tipo_server", ""), count, detalles_texto, fila.get("ubicacion", ""))
                )
            elif hostname in ad_inv.iloc[:, 0].values:
                fila = ad_inv[ad_inv.iloc[:, 0] == hostname].iloc[0]
                resultado["Microsoft AD"].append(
                    (hostname, fila.get("tipo_server", ""), count, detalles_texto, fila.get("ubicacion", ""))
                )
            else:
                resultado["OTROS"].append((hostname, "", count, detalles_texto, ""))

        # ---------- REPORTE EN TEXTO (SIN GUARDAR) ----------
        fecha_actual = datetime.now()
        fecha_inicio = fecha_actual - timedelta(days=7)

        rep = []
        rep.append(f"{fecha_actual.strftime('%d/%m/%Y')}\n")
        rep.append(
            f"Se realiza análisis del TOP 5 de los servidores con más incidentes entre "
            f"{fecha_inicio.strftime('%d/%m/%Y')} y {fecha_actual.strftime('%d/%m/%Y')}:\n"
        )

        for doliente, servers in resultado.items():
            if not servers:
                continue

            rep.append(f"\nDoliente: {doliente} [")
            for i, (h, t, c, d, u) in enumerate(servers, 1):
                linea = f"\t{i:02d}. {h}"
                if t:
                    linea += f" ({t})"
                linea += f": {c} casos"
                if d:
                    linea += f" ({d})"
                rep.append(linea)
                if u:
                    rep.append(f"\tNOTA: {u} \n")
            rep.append("]")

        return "\n".join(rep)

    except Exception as e:
        return f"Error ejecutando Top5: {e}"
