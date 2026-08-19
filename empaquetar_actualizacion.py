import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from version import VERSION  # noqa: E402

SRC = os.path.join("dist", "distribucion", "RongonLang Launcher")
OUT_ZIP = os.path.join("dist", "distribucion", f"launcher_update_{VERSION}.zip")
OUT_JSON = os.path.join("dist", "distribucion", "version.json")


def main():
    exe = os.path.join(SRC, "RongonLang Launcher.exe")
    internal = os.path.join(SRC, "_internal")
    if not os.path.isfile(exe) or not os.path.isdir(internal):
        print(f"ERROR: no existe el exe o _internal en {SRC}")
        return 1

    if os.path.exists(OUT_ZIP):
        os.remove(OUT_ZIP)

    count = 0
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(exe, "RongonLang Launcher.exe")
        count += 1
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
    print(f"  1) Crea una Release 'v{VERSION}' en https://github.com/{'rongorus1/launcher-minecraft-v1'}/releases")
    print(f"  2) Sube como asset: {os.path.basename(OUT_ZIP)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())