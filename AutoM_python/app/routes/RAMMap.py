import os
import subprocess
import sys
import ctypes


def is_admin():
    """Verifica si el script se ejecuta con privilegios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def EjcRAMMap():
    """RUTA DE APP"""
    rammap_path = r"D:\Repo\PoweShell EXP\app\utilitarios\RAMMap\RAMMap.exe"

    # Validar existencia
    if not os.path.exists(rammap_path):
        print(f"❌ No se encontró RAMMap en {rammap_path}")
        return

    # Comandos que queremos ejecutar (todos menos paginación)
    commands = ["-Ew", "-Es", "-Et"]

    # Si no tiene permisos, se relanza automáticamente con admin
    if not is_admin():
        print("🔒 Elevando permisos para ejecutar RAMMap...")
        # Relanza este mismo archivo como administrador
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )
        return

    # Si ya estamos como admin, ejecutamos normalmente
    print("🚀 Ejecutando limpieza de memoria RAM (sin paginación)...")
    for cmd in commands:
        print(f"🧹 Ejecutando RAMMap con {cmd} ...")
        subprocess.run([rammap_path, cmd, "/accepteula"], shell=True)

    print("✅ Limpieza de memoria completada.\n")
