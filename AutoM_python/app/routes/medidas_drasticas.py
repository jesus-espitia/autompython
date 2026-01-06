import os
import re
from datetime import datetime

def medidasDrasticas():
    try:
        # ---------- RUTAS RELATIVAS ----------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        txt_dir = os.path.join(project_root, "Ruta-TXT")

        # ---------- OBTENER ARCHIVO MÁS RECIENTE ----------
        archivos = []
        for f in os.listdir(txt_dir):
            m = re.match(r"Reporte_Incidentes_(\d{2}-\d{2}-\d{4})\.txt", f)
            if m:
                fecha = datetime.strptime(m.group(1), "%d-%m-%Y")
                archivos.append((fecha, f))

        if not archivos:
            print("❌ No se encontraron reportes.")
            return

        archivo_actual = max(archivos, key=lambda x: x[0])[1]
        ruta_archivo = os.path.join(txt_dir, archivo_actual)

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        # ---------- REGLAS POR TIPO (NO LITERALES) ----------
        reglas = {
            "memory": [
                "procesamiento de imágenes PACS",
                "Saturación de componente"
            ],
            "cpu": [
                "procesamiento de imágenes PACS",
                "Saturación de componente"
            ],
            "server down": [
                "Problemas con el componente de red",
                "Desconexión momentánea con el agente"
            ],
            "reboot": [
                "Reinicio inesperado",
                "Reinicio por actualización"
            ],
            "storage": [
                "Depuración de logs y archivos innecesarios"
            ],
            "disk": [
                "Depuración de logs y archivos innecesarios"
            ],
            "space": [
                "Depuración de logs y archivos innecesarios"
            ],
        }

        salida = []
        en_infra = False
        es_pacs = False
        texto_desc = ""

        for linea in lineas:

            # Detectar doliente
            if linea.startswith("Doliente:"):
                en_infra = "Microsoft Infra" in linea
                salida.append(linea)
                continue

            # Detectar servidor PACS
            if en_infra and "(PACS)" in linea:
                es_pacs = True
                # Capturar TODO lo que está entre el último paréntesis
                m = re.search(r"\(([^()]*)\)\s*$", linea)
                texto_desc = m.group(1).lower() if m else ""
                salida.append(linea)
                continue

            # Detectar NOTA
            if es_pacs and linea.strip().startswith("NOTA:"):
                notas_detectadas = set()

                for clave, notas in reglas.items():
                    if clave in texto_desc:
                        # Elegir SOLO UNA nota por tipo
                        notas_detectadas.add(notas[0])

                notas_existentes = linea.replace("NOTA:", "").strip()

                notas_finales = []
                if notas_existentes:
                    notas_finales.append(notas_existentes)
                if notas_detectadas:
                    notas_finales.append(", ".join(sorted(notas_detectadas)))

                salida.append("\tNOTA: " + ", ".join(notas_finales) + "\n")

                # Reset
                es_pacs = False
                texto_desc = ""
                continue

            salida.append(linea)

        # ---------- GUARDAR ----------
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.writelines(salida)

        print(f"✅ NOTAS DE EMERGENCIA COMPLETADAS EN: {archivo_actual}")

    except Exception as e:
        print(f"❌ Error ejecutando medidasDrasticas: {e}")
