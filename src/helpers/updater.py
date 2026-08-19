import hashlib
import logging
import os
import shutil
import subprocess
import sys
import zipfile

import requests

from services.logging_service import config_logging


def _es_version_superior(nueva: str, actual: str) -> bool:
    """Compara versiones semver simples: '1.0.1' > '1.0.0'."""
    def partes(v: str):
        out = []
        for p in str(v).split("."):
            num = ""
            for ch in p:
                if ch.isdigit():
                    num += ch
                else:
                    break
            out.append(int(num) if num else 0)
        return out

    a, b = partes(actual), partes(nueva)
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else 0
        y = b[i] if i < len(b) else 0
        if y > x:
            return True
        if y < x:
            return False
    return False


def version_remota(repo: str):
    """Consulta la ultima release de GitHub. Devuelve (version, asset) o (None, None)."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    r = requests.get(url, headers={"User-Agent": "RongonLang-Launcher"}, timeout=(10, 20))
    if r.status_code != 200:
        return None, None
    data = r.json()
    tag = str(data.get("tag_name", "")).lstrip("v")
    asset = None
    for a in data.get("assets", []):
        if a.get("name", "").startswith("launcher_update_"):
            asset = a
            break
    return tag, asset


def descargar_actualizacion(asset, destino: str):
    logging.getLogger().info(f"Descargando actualizacion: {asset.get('name')}")
    r = requests.get(asset["browser_download_url"], stream=True, timeout=(15, 300))
    r.raise_for_status()
    with open(destino, "wb") as f:
        shutil.copyfileobj(r.raw, f)

    digest = asset.get("digest")
    if digest:
        sha = str(digest).split(":", 1)[-1]
        with open(destino, "rb") as f:
            real = hashlib.sha256(f.read()).hexdigest().lower()
        if real != sha.lower():
            raise RuntimeError("El hash de la actualizacion no coincide (descarga corrupta)")


def _extraer_seguro(z, destino: str):
    base = os.path.abspath(destino)
    for m in z.infolist():
        if m.is_dir():
            continue
        nombre = m.filename.replace("\\", "/")
        if nombre.startswith("/") or ".." in nombre.split("/"):
            continue
        target = os.path.join(base, nombre.replace("/", os.sep))
        if not os.path.abspath(target).startswith(base + os.sep):
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with z.open(m) as src, open(target, "wb") as dst:
            shutil.copyfileobj(src, dst)


def aplicar_actualizacion(zip_path: str) -> str:
    """Prepara el swap y devuelve la ruta del .bat que aplicara el cambio al cerrar."""
    config_logging()
    logger = logging.getLogger()
    base = os.path.dirname(sys.executable)

    update_dir = os.path.join(base, "_update")
    if os.path.isdir(update_dir):
        shutil.rmtree(update_dir, ignore_errors=True)
    os.makedirs(update_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path) as z:
        _extraer_seguro(z, update_dir)

    exe_new = os.path.join(base, "RongonLang Launcher.exe.new")
    internal_new = os.path.join(base, "_internal.new")

    for origen, destino in ((os.path.join(update_dir, "RongonLang Launcher.exe"), exe_new),
                            (os.path.join(update_dir, "_internal"), internal_new)):
        if not os.path.exists(origen):
            logger.warning(f"El paquete de actualizacion no trae {os.path.basename(origen)}")
            continue
        if os.path.exists(destino):
            if os.path.isdir(destino):
                shutil.rmtree(destino, ignore_errors=True)
            else:
                os.remove(destino)
        os.rename(origen, destino)

    shutil.rmtree(update_dir, ignore_errors=True)

    bat = os.path.join(base, "actualizar.bat")
    with open(bat, "w", encoding="utf-8") as f:
        f.write(
            "@echo off\r\n"
            'cd /d "%~dp0"\r\n'
            ":espera\r\n"
            'tasklist /fi "IMAGENAME eq RongonLang Launcher.exe" 2>nul | find /i "RongonLang Launcher.exe" >nul\r\n'
            "if not errorlevel 1 (\r\n"
            "  timeout /t 1 /nobreak >nul\r\n"
            "  goto espera\r\n"
            ")\r\n"
            'if exist "_internal.new" (\r\n'
            '  if exist "_internal.old" rmdir /s /q "_internal.old"\r\n'
            '  ren "_internal" "_internal.old" 2>nul\r\n'
            '  ren "_internal.new" "_internal" 2>nul\r\n'
            '  if exist "_internal.old" rmdir /s /q "_internal.old"\r\n'
            ")\r\n"
            'if exist "RongonLang Launcher.exe.new" (\r\n'
            '  ren "RongonLang Launcher.exe" "RongonLang Launcher.exe.old" 2>nul\r\n'
            '  ren "RongonLang Launcher.exe.new" "RongonLang Launcher.exe" 2>nul\r\n'
            '  if exist "RongonLang Launcher.exe.old" del /q "RongonLang Launcher.exe.old"\r\n'
            ")\r\n"
            'start "" "RongonLang Launcher.exe"\r\n'
            'del /q "%~f0"\r\n'
        )
    return bat


def lanzar_actualizacion(bat: str):
    base = os.path.dirname(sys.executable)
    subprocess.Popen(["cmd", "/c", bat], cwd=base, creationflags=subprocess.CREATE_NO_WINDOW)