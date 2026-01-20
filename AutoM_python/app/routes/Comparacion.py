import pandas as pd
import os
import re
from datetime import datetime

def comparar_reporte_infra():
    try:
        print("🔍 Comparando REPORTE contra INVENTARIOS (Infra / AD)\n")

        # ==================================================
        # 📁 RUTAS (MISMO ESTILO QUE topDeInicidentes)
        # ==================================================
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        csv_dir = os.path.join(project_root, "Ruta-CSV")
        txt_dir = os.path.join(project_root, "Ruta-TXT")
        excel_dir = os.path.join(project_root, "Excel", "ARCHIVOS_ALIMENTADORES_INFRA_AD")

        infra_file = os.path.join(excel_dir, "INVENTARIO_INFRA_beta.xlsx")
        ad_file = os.path.join(excel_dir, "INVENTARIO_AD_beta.xlsx")

        # ==================================================
        # 🔧 NORMALIZADOR (MISMA IDEA QUE TU CÓDIGO)
        # ==================================================
        def normalizar_servidor(v):
            if pd.isna(v):
                return None
            return str(v).strip().upper().split(".")[0]

        # ==================================================
        # 📚 CARGAR INVENTARIOS
        # ==================================================
        def cargar_inventario(path):
            if not os.path.exists(path):
                return pd.DataFrame()

            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]

            df = df[df.iloc[:, 0].notna()]
            df.iloc[:, 0] = df.iloc[:, 0].apply(normalizar_servidor)

            return df

        infra_inv = cargar_inventario(infra_file)
        ad_inv = cargar_inventario(ad_file)

        # ==================================================
        # 📄 SELECCIONAR REPORTE (Ruta-CSV)
        # ==================================================
        reportes = [
            f for f in os.listdir(csv_dir)
            if f.lower().endswith((".csv", ".xlsx", ".xls"))
        ]

        if not reportes:
            print("❌ No hay reportes en Ruta-CSV")
            return

        print("📄 Reportes disponibles:\n")
        for i, r in enumerate(reportes, 1):
            print(f"{i}. {r}")

        opcion = int(input("\nSelecciona el reporte a comparar: "))
        reporte_usado = reportes[opcion - 1]
        ruta_reporte = os.path.join(csv_dir, reporte_usado)

        # ==================================================
        # 📊 CARGAR REPORTE
        # ==================================================
        df_rep = (
            pd.read_csv(ruta_reporte)
            if ruta_reporte.lower().endswith(".csv")
            else pd.read_excel(ruta_reporte)
        )

        columnas_originales = df_rep.columns.tolist()

        print("\n📌 Columnas disponibles:\n")
        for c in columnas_originales:
            print(f"- {c}")

        col_map = {
            re.sub(r"\s+", " ", c).strip().lower(): c
            for c in columnas_originales
        }

        while True:
            col_input = input("\nCopia el nombre EXACTO de la columna con servidores: ").strip()
            key = re.sub(r"\s+", " ", col_input).strip().lower()
            if key in col_map:
                col_servidor = col_map[key]
                break
            print("❌ Columna inválida")

        servidores_reporte = (
            df_rep[col_servidor]
            .apply(normalizar_servidor)
            .dropna()
            .unique()
        )

        # ==================================================
        # 🔁 CLASIFICAR (MISMA LÓGICA DEL TOP)
        # ==================================================
        resultado = {
            "Microsoft Infra": [],
            "Microsoft AD": [],
            "OTROS": []
        }

        for srv in servidores_reporte:
            if srv in infra_inv.iloc[:, 0].values:
                fila = infra_inv[infra_inv.iloc[:, 0] == srv].iloc[0]
                tipo = fila.get("tipo_server", "SIN TIPO")
                resultado["Microsoft Infra"].append((srv, tipo))

            elif srv in ad_inv.iloc[:, 0].values:
                fila = ad_inv[ad_inv.iloc[:, 0] == srv].iloc[0]
                tipo = fila.get("tipo_server", "SIN TIPO")
                resultado["Microsoft AD"].append((srv, tipo))

            else:
                resultado["OTROS"].append((srv, "SIN TIPO"))

        # ==================================================
        # 📝 GENERAR TXT (MISMO FORMATO CONCEPTUAL)
        # ==================================================
        os.makedirs(txt_dir, exist_ok=True)

        fecha = datetime.now().strftime("%d-%m-%Y")
        salida = os.path.join(txt_dir, f"Comparacion_Infra_AD_{fecha}.txt")

        rep = []
        rep.append(f"{fecha}\n")
        rep.append(f"Reporte analizado: {reporte_usado}")
        rep.append(f"Columna comparada: {col_servidor}\n")

        for doliente, servidores in resultado.items():
            if not servidores:
                continue

            rep.append(f"\nDoliente: {doliente} [")
            for i, (srv, tipo) in enumerate(servidores, 1):
                rep.append(f"\t{i:02d}. {srv} ({tipo})")
            rep.append("]")

        with open(salida, "w", encoding="utf-8") as f:
            f.write("\n".join(rep))

        print(f"\n📝 Reporte generado correctamente en:\n{salida}\n\n")
        print("☝🏻☝🏻 Este archivo no es necesario en el repositorio. Elimínalo cuando ya no sea necesario... ☝🏻☝🏻")

    except Exception as e:
        print(f"❌ Error ejecutando comparar_reporte_infra: {e}")
