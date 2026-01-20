import pandas as pd
import os

def InfoServers():
    try:
        print("🔍 Consulta interactiva de servidores")
        print("✏️ Escribe el nombre del servidor o 'SALIR' para terminar\n")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        excel_dir = os.path.join(project_root, "Excel", "ARCHIVOS_ALIMENTADORES_INFRA_AD")

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

        # ---------- FUNCIÓN PARA MOSTRAR INFO ----------
        def mostrar_info(fila):
            print(f"\n 🖥️ Nombre Servidor: {fila.iloc[0]}")

            if fila.get("direccion ip"):
                print(f"🌐 Dirección IP: {fila['direccion ip']}")

            if fila.get("conexion"):
                print(f"🔌 Conexión: {fila['conexion']}")

            if fila.get("doliente"):
                print(f"👤 Doliente: {fila['doliente']}")

            if fila.get("tipo_server"):
                print(f"🧩 Tipo Server: {fila['tipo_server']}")

            if fila.get("ambiente"):
                print(f"🏷️ Ambiente: {fila['ambiente']}")

            if fila.get("ubicacion"):
                print(f"📍 Ubicación: {fila['ubicacion']}")

        # ---------- BUCLE PRINCIPAL ----------
        while True:
            server = input("\n 🖥️ Escribe el nombre del servidor o Salir: ").strip().upper()

            if server == "SALIR":
                print("\n👋 Saliendo de la consulta de servidores.")
                break

            encontrado = False

            # Buscar en Infra
            if not infra_inv.empty and server in infra_inv.iloc[:, 0].values:
                fila = infra_inv[infra_inv.iloc[:, 0] == server].iloc[0]
                print("\n📂 Inventario: Microsoft Infra")
                mostrar_info(fila)
                encontrado = True

            # Buscar en AD
            if not ad_inv.empty and server in ad_inv.iloc[:, 0].values:
                fila = ad_inv[ad_inv.iloc[:, 0] == server].iloc[0]
                print("\n📂 Inventario: Microsoft AD")
                mostrar_info(fila)
                encontrado = True

            if not encontrado:
                print("\n❌ Servidor no encontrado en los inventarios.")

    except Exception as e:
        print(f"❌ Error ejecutando Info_Servers: {e}")
