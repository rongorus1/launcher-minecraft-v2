import json
import os
import sys
import zipfile

# Añadir src/ al path para importaciones durante el build
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from version import VERSION, GITHUB_REPO  # noqa: E402

# build.bat already does: cd /d "%~dp0" (launcher root directory)
# Por lo tanto, rutas relativas desde aquí apuntan a la carpeta correcta.
PROJECT_ROOT = os.path.abspath(".")

# Determinar modo y directorio base:
# - Si sys._MEIPASS existe: modo PyInstaller onefile (exe incrustado, recursos en _MEIPASS)
# - Si no: modo onedir o desarrollo
if getattr(sys, "_MEIPASS", None):
    # Modo onefile: PyInstaller extrae a _MEIPASS al ejecutarse
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    # En modo onefile, los archivos "internos" los deja PyInstaller en _MEIPASS
    INTERNAL_DIR = sys._MEIPASS
else:
    # Modo onedir o desarrollo: la estructura de carpetas normal
    BASE_DIR = os.path.abspath(os.path.join(".", "dist", "distribucion", "RongonLang Launcher"))
    INTERNAL_DIR = os.path.join(BASE_DIR, "_internal")

OUT_ZIP = os.path.abspath(os.path.join("dist", "distribucion", f"launcher_update_{VERSION}.zip"))
OUT_JSON = os.path.abspath(os.path.join("dist", "distribucion", "version.json"))


def main():
    # Determinar rutas del exe y carpetas según el modo
    if getattr(sys, "_MEIPASS", None):
        # Modo onefile: el exe está en la misma dir que sys.executable (o _MEIPASS)
        exe = os.path.join(BASE_DIR, "RongonLang Launcher.exe")
        # Para el modo onefile, intentamos usar _MEIPASS que PyInstaller crea al ejecutarse
        # Los archivos _internal los deja PyInstaller en _MEIPASS/RongonLang Launcher/_internal o similar
        internal = os.path.join(INTERNAL_DIR, "RongonLang Launcher", "_internal") if os.path.isdir(
            os.path.join(INTERNAL_DIR, "RongonLang Launcher")) else INTERNAL_DIR
        # Verificar si el exe existe físicamente en BASE_DIR
        if not os.path.isfile(exe):
            # Si no existe, puede que aún no hayamos lanzado el exe, así que buscamos en la ruta conocida
            exe = os.path.abspath(os.path.join("dist", "distribucion", "RongonLang Launcher.exe"))
            internal = os.path.join(os.path.abspath("dist"), "distribucion", "RongonLang Launcher", "_internal")
    else:
        # Modo onedir o desarrollo
        exe = os.path.join(BASE_DIR, "RongonLang Launcher.exe")
        internal = INTERNAL_DIR

    # Verificar que el exe y internal existen
    if not os.path.isfile(exe):
        # Último intento: buscar en dist\distribucion\ (ruta esperada después del build)
        alt_exe = os.path.abspath(os.path.join("dist", "distribucion", "RongonLang Launcher.exe"))
        if os.path.isfile(alt_exe):
            exe = alt_exe
            # Para onedir, _internal está en la misma carpeta que el exe
            internal = os.path.join(os.path.dirname(alt_exe), "_internal")
        else:
            print(f"ERROR: no se encuentra el exe. Intentado: {exe}")
            return 1
    elif not os.path.isdir(internal):
        # Modo onefile: _internal no existe como carpeta, los recursos están incrustados.
        # Creamos un directorio temporal con la estructura esperada o nos saltamos la validación
        # y creamos el zip directamente del exe.
        internal = None  # Indicar modo onefile

    # Si internal es None (modo onefile), creamos el zip solo con el exe
    # y esperamos que al ejecutarse, PyInstaller despliegue los archivos internos
    if internal is None:
        # Modo onefile: el exe está incrustado, creamos zip con solo el exe
        # y el updater se encargará de extraer los archivos internos al ejecutarse
        if os.path.exists(OUT_ZIP):
            os.remove(OUT_ZIP)
        with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(exe, "RongonLang Launcher.exe")
        count = 1
    else:
        # Modo onedir: empaquetar exe + _internal como de costumbre
        if os.path.exists(OUT_ZIP):
            os.remove(OUT_ZIP)
        with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(exe, "RongonLang Launcher.exe")
            count = 1
            for root, _, files in os.walk(internal):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.join("_internal", os.path.relpath(full, internal))
                    z.write(full, rel.replace(os.sep, "/"))
                    count += 1

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "update": f"launcher_update_{VERSION}.zip"}, f, indent=2)

    size = os.path.getsize(OUT_ZIP) / 1024 / 1024
    print(f"Paquete de actualizacion: {OUT_ZIP} ({count} archivos, {size:.1f} MB)")
    print("Para publicar:")
    print(f"  1) Crea una Release 'v{VERSION}' en https://github.com/{GITHUB_REPO}/releases")
    print(f"  2) Sube como asset: {os.path.basename(OUT_ZIP)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
