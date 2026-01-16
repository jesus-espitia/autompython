import pandas as pd
import os
import re

def detectar_accesos_criticos():
    try:
        print("🔍 Ejecutando análisis de accesos críticos...\n")

        # ==================================================
        # 📁 DEFINIR RUTAS RELATIVAS DEL PROYECTO
        # ==================================================
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        csv_dir = os.path.join(project_root, "Ruta-CSV")

        if not os.path.exists(csv_dir):
            print("❌ La carpeta Ruta-CSV no existe.")
            return

        # ==================================================
        # 📄 LISTAR ARCHIVOS CSV / EXCEL
        # ==================================================
        archivos = [
            f for f in os.listdir(csv_dir)
            if f.lower().endswith((".csv", ".xlsx", ".xls"))
            and not f.startswith("~$")
        ]

        if not archivos:
            print("❌ No se encontraron archivos CSV o Excel.")
            return

        print(f"📑 Archivos encontrados ({len(archivos)}):\n")
        for i, f in enumerate(archivos, 1):
            print(f"{i}. {f}")

        opcion = input("\nSelecciona un archivo por número: ").strip()
        if not opcion.isdigit() or not (1 <= int(opcion) <= len(archivos)):
            print("❌ Selección inválida.")
            return

        ruta_archivo = os.path.join(csv_dir, archivos[int(opcion) - 1])

        # ==================================================
        # 📊 CARGAR ARCHIVO
        # ==================================================
        if ruta_archivo.lower().endswith(".csv"):
            df = pd.read_csv(ruta_archivo)
        else:
            df = pd.read_excel(ruta_archivo)

        if df.empty:
            print("❌ El archivo está vacío.")
            return

        columnas_originales = df.columns.tolist()

        print("\n📌 Columnas disponibles:\n")
        for c in columnas_originales:
            print(f"- {c}")

        col_map = {
            re.sub(r"\s+", " ", c).strip().lower(): c
            for c in columnas_originales
        }

        # ==================================================
        # 🔁 SELECCIÓN DE COLUMNA A ANALIZAR
        # ==================================================
        while True:
            col = input(
                "\nCopia EXACTAMENTE el nombre de la columna a analizar: "
            ).strip()

            key = re.sub(r"\s+", " ", col).strip().lower()

            if key not in col_map:
                print("❌ La columna no existe.")
                continue
            break

        columna_objetivo = col_map[key]
        print(f"\n✅ Columna seleccionada: {columna_objetivo}")

        # ==================================================
        # 🚨 DETECTAR ACCESOS CRÍTICOS
        # ==================================================
        valores_criticos = ("DOMAIN USER", "EVERYONE")

        df_tmp = df.copy()
        df_tmp[columna_objetivo] = (
            df_tmp[columna_objetivo]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df_criticos = df_tmp[
            df_tmp[columna_objetivo]
            .str.contains("|".join(valores_criticos), regex=True, na=False)
        ]

        if df_criticos.empty:
            print("\n✅ No se encontraron accesos críticos.")
            return

        # ==================================================
        # 📤 EXPORTAR RESULTADO A NUEVO EXCEL
        # ==================================================
        nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
        salida = os.path.join(
            csv_dir,
            f"ACCESOS_CRITICOS_{nombre_base}.xlsx"
        )

        with pd.ExcelWriter(salida, engine="openpyxl") as writer:
            df_criticos.to_excel(
                writer,
                sheet_name="CRITICOS_ACCESOS",
                index=False
            )

        print("\n🚨 Accesos críticos encontrados.")
        print(f"📄 Archivo generado correctamente:\n{salida}\n")

    except Exception as e:
        print(f"❌ Error ejecutando detectar_accesos_criticos: {e}")
