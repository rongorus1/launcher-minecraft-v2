import os
import re
import sys
import zipfile

# Añadir src/ al path para importaciones durante el build
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from helpers.system_tools import get_resource_path

MC_DIR = os.path.expanduser("~/Desktop/RongocraftLauncher/.minecraft")
ZIP_OUT = os.path.join("dist", "distribucion", "RongonLang Launcher", "juego_preinstalado.zip")
DIRS = ("versions", "libraries", "assets", "runtime")

CONFIG = os.path.join("src", "config", "__init__.py")


def _leer_version(nombre):
    with open(CONFIG, encoding="utf-8") as f:
        m = re.search(rf'{nombre} = "([^"]+)"', f.read())
    return m.group(1) if m else None


def main():
    mc = _leer_version("MINECRAFT_VERSION")
    forge = _leer_version("FORGE_VERSION")
    profile = f"{mc}-forge-{forge}"
    marker = os.path.join(MC_DIR, "versions", profile, f"{profile}.json")
    if not os.path.isfile(marker):
        print(f"AVISO: el juego instalado no se encontro en {MC_DIR}; se omite el zip.")
        print(f"  (esperado: versions\\{profile}\\{profile}.json)")
        return 0

    os.makedirs(os.path.dirname(ZIP_OUT), exist_ok=True)
    if os.path.exists(ZIP_OUT):
        os.remove(ZIP_OUT)

    # Determinar directorio base: modo onefile usa _MEIPASS, modoonedir usa la carpeta
    if getattr(sys, "_MEIPASS", None):
        # Modo PyInstaller onefile: los archivos estan en _MEIPASS
        base_dir = get_resource_path("")
        zip_inside = os.path.join(base_dir, "juego_preinstalado.zip")
        if os.path.isfile(zip_inside):
            import shutil
            shutil.copy2(zip_inside, ZIP_OUT)
            print(f"Zip creado copiando desde el exe empaquetado: {ZIP_OUT}")
            return 0
        else:
            print("AVISO: No se encontró juego_preinstalado.zip dentro del exe (puede que aún no esté integrado).")
            return 0

    # Modo desarrollo o carpetaonedir: buscar el zip generado por empaquetado anterior
    # o crear uno nuevo desde el directorio del juego instalado
    os.makedirs(os.path.dirname(ZIP_OUT), exist_ok=True)
    if os.path.exists(ZIP_OUT):
        os.remove(ZIP_OUT)

    count = 0
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for d in DIRS:
            p = os.path.join(MC_DIR, d)
            if not os.path.isdir(p):
                print(f"AVISO: falta la carpeta {d} en el juego instalado.")
                continue
            for root, _, fs in os.walk(p):
                for f in fs:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, MC_DIR)
                    z.write(full, rel.replace(os.sep, "/"))
                    count += 1
                    if count % 3000 == 0:
                        print(f"  {count} archivos...")

    size = os.path.getsize(ZIP_OUT) / 1024 / 1024
    print(f"Zip creado: {ZIP_OUT} ({count} archivos, {size:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())