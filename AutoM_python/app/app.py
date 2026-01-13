import importlib
import os
import sys

# === CONFIGURACIÓN DE RUTAS ===
BASE_DIR = os.path.dirname(__file__)
RUTA_MODULOS = os.path.join(BASE_DIR, "routes")


# Asegura que el directorio padre (el que contiene "app") esté en sys.path
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
    
# Aseguramos que Python pueda importar desde la carpeta base
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Mapa de módulos y funciones a ejecutar
FUNCIONES_PRINCIPALES = {
    "top5_incidentes": "topDeInicidentes",
    "Formato_Fechas_Horas":"separar_fecha_hora_columnas_dinamicas",
    "medidas_drasticas":"medidasDrasticas",
}


def listar_modulos():
    """Devuelve lista de archivos .py en routes."""
    return [
        f[:-3] for f in os.listdir(RUTA_MODULOS)
        if f.endswith(".py") and not f.startswith("__")
    ]

def ejecutar_modulo(nombre_modulo):
    """Importa y ejecuta la función asociada en FUNCIONES_PRINCIPALES."""
    try:
        print(f"\n🚀 Ejecutando módulo: {nombre_modulo}\n")

        # Import dinámico
        modulo = importlib.import_module(f"app.routes.{nombre_modulo}")

        # Verificar que tenga función asociada
        funcion = FUNCIONES_PRINCIPALES.get(nombre_modulo)
        if not funcion:
            print(f"⚠️ No se ha configurado la función principal para '{nombre_modulo}'")
            return

        if not hasattr(modulo, funcion):
            print(f"❌ El módulo '{nombre_modulo}' no contiene la función '{funcion}'")
            return

        # Ejecutar
        getattr(modulo, funcion)()
        print(f"✅ Módulo '{nombre_modulo}' ejecutado correctamente.\n")

    except Exception as e:
        print(f"❌ Error ejecutando '{nombre_modulo}': {e}\n")

def mostrar_menu(modulos):
    print("\n===========================================")
    print("💻  ¿QUÉ DESEAS HACER HOY?")
    print("===========================================")
    for i, mod in enumerate(modulos, 1):
        print(f"{i}. {mod}")
    print("0. Salir")
    print("===========================================")

if __name__ == "__main__":
    modulos = listar_modulos()

    if not modulos:
        print("⚠️ No hay módulos en 'routes'.")
        sys.exit()

    while True:
        mostrar_menu(modulos)
        opcion = input("👉 Ingresa el número del módulo a ejecutar: ").strip()

        if not opcion.isdigit():
            print("⚠️ Por favor ingresa un número válido.")
            continue

        opcion = int(opcion)
        if opcion == 0:
            print("👋 Saliendo...")
            break
        elif 1 <= opcion <= len(modulos):
            ejecutar_modulo(modulos[opcion - 1])
        else:
            print("❌ Opción no válida.")
