import os
import zipfile

SRC = os.path.join("dist", "distribucion", "RongonLang Launcher")
OUT = os.path.join("dist", "distribucion", "RongonLang Launcher.zip")


def main():
    if not os.path.isdir(SRC):
        print(f"ERROR: no existe la carpeta {SRC}")
        return 1
    if os.path.exists(OUT):
        os.remove(OUT)

    count = 0
    with zipfile.ZipFile(OUT, "w") as z:
        for root, _, files in os.walk(SRC):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, os.path.dirname(SRC))
                # El juego preinstalado ya esta comprimido: guardarlo sin re-comprimir
                if f == "juego_preinstalado.zip":
                    z.write(full, rel, compress_type=zipfile.ZIP_STORED)
                else:
                    z.write(full, rel, compress_type=zipfile.ZIP_DEFLATED)
                count += 1

    size = os.path.getsize(OUT) / 1024 / 1024
    print(f"OK: {OUT} ({count} archivos, {size:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())