import re

def descripcion_inc(texto_reporte):
    try:
        lineas = texto_reporte.splitlines(keepends=True)

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
                "Desconexión momentánea con el agente de SolarWinds"
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

            if linea.startswith("Doliente:"):
                en_infra = "Microsoft Infra" in linea
                salida.append(linea)
                continue

            if en_infra and "(PACS)" in linea:
                es_pacs = True
                m = re.search(r"\(([^()]*)\)\s*$", linea)
                texto_desc = m.group(1).lower() if m else ""
                salida.append(linea)
                continue

            if es_pacs and linea.strip().startswith("NOTA:"):
                notas_detectadas = set()

                for clave, notas in reglas.items():
                    if clave in texto_desc:
                        notas_detectadas.add(notas[0])

                notas_existentes = linea.replace("NOTA:", "").strip()

                notas_finales = []
                if notas_existentes:
                    notas_finales.append(notas_existentes)
                if notas_detectadas:
                    notas_finales.append(", ".join(sorted(notas_detectadas)))

                salida.append("\tNOTA: " + ", ".join(notas_finales) + "\n")

                es_pacs = False
                texto_desc = ""
                continue

            salida.append(linea)

        return "".join(salida)

    except Exception as e:
        return f"Error aplicando descripción INC: {e}"
