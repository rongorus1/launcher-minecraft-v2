import os
import sys
import zipfile

MC_DIR = os.path.expanduser("~/Desktop/RongocraftLauncher/.minecraft")
ZIP_OUT = os.path.join("dist", "distribucion", "RongonLang Launcher", "juego_preinstalado.zip")
DIRS = ("versions", "libraries", "assets", "runtime")


def main():
    marker = os.path.join(MC_DIR, "versions", "1.20.1-forge-47.3.0", "1.20.1-forge-47.3.0.json")
    if not os.path.isfile(marker):
        print(f"AVISO: el juego instalado no se encontro en {MC_DIR}; se omite el zip.")
        return 0

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