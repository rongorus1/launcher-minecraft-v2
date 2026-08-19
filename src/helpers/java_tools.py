import os
import platform
import re
import shutil
import subprocess
import tarfile
import zipfile
from tkinter import messagebox

import requests

from config import LAUNCHER_DIR


def _ruta_java_launcher():
    return os.path.join(LAUNCHER_DIR, "Java", "java17", "bin", "java.exe" if platform.system() == "Windows" else "java")


def _version_java(java_path):
    """Devuelve la versión principal de un binario de Java (0 si no se puede leer)."""
    try:
        out = subprocess.run([java_path, "-version"], capture_output=True, text=True, timeout=10)
        texto = out.stderr or out.stdout
        match = re.search(r'"(\d+)', texto)
        if match:
            version = int(match.group(1))
            return 8 if version == 1 else version  # "1.8.0" -> 8
    except Exception:
        pass
    return 0


def _java_en_path():
    """Devuelve la ruta de 'java' en el PATH si es versión 17 o superior, o None."""
    ruta = shutil.which("java")
    if ruta and _version_java(ruta) >= 17:
        return ruta
    return None


def descargar_java_17():
    """Descargar e instalar Temurin 17 (JRE) en la carpeta del launcher.

    No requiere herramientas externas: zip para Windows, tar.gz para macOS/Linux.
    """
    try:
        java_dir = os.path.join(LAUNCHER_DIR, "Java")
        java17_dir = os.path.join(java_dir, "java17")
        os.makedirs(java_dir, exist_ok=True)

        binario = _ruta_java_launcher()
        if os.path.exists(binario):
            return True

        sistema_actual = platform.system()
        urls = {
            "Windows": "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse",
            "Darwin": "https://api.adoptium.net/v3/binary/latest/17/ga/mac/x64/jre/hotspot/normal/eclipse",
            "Linux": "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jre/hotspot/normal/eclipse",
        }
        java_url = urls.get(sistema_actual, urls["Windows"])

        messagebox.showinfo("Instalación de Java", "Descargando Java 17. Esto puede tardar unos minutos...")

        respuesta = requests.get(java_url, stream=True, allow_redirects=True, timeout=60)
        respuesta.raise_for_status()
        ruta_descarga = os.path.join(java_dir, "java17_tmp")
        with open(ruta_descarga, 'wb') as archivo:
            for fragmento in respuesta.iter_content(chunk_size=8192):
                archivo.write(fragmento)

        # Extraer a un directorio temporal para luego dejar solo java17/
        temp_dir = os.path.join(java_dir, "java17_tmp_dir")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)

        if sistema_actual == "Windows":
            with zipfile.ZipFile(ruta_descarga, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        else:
            with tarfile.open(ruta_descarga, 'r:gz') as tar_ref:
                tar_ref.extractall(temp_dir)

        os.remove(ruta_descarga)

        # Mover la carpeta extraída (el nombre varía según la versión) a java17/
        for nombre in os.listdir(temp_dir):
            origen = os.path.join(temp_dir, nombre)
            if os.path.isdir(origen):
                if os.path.exists(java17_dir):
                    shutil.rmtree(java17_dir, ignore_errors=True)
                shutil.move(origen, java17_dir)
                break

        shutil.rmtree(temp_dir, ignore_errors=True)

        if os.path.exists(_ruta_java_launcher()):
            messagebox.showinfo("Éxito", "Java 17 se ha instalado correctamente")
            return True

        messagebox.showerror("Error", "No se pudo instalar Java automáticamente")
        return False

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo instalar Java: {e}")
        return False


def detectar_java():
    """Detectar Java 17 para ejecutar Minecraft.

    Prioridad:
      1. java en el PATH del sistema
      2. Java ya descargado por el launcher (Java/java17)
      3. Descarga automática de Temurin 17
    """
    try:
        # 1) Java del sistema
        java_path = _java_en_path()
        if java_path:
            return java_path

        # 2) Java del launcher
        ruta_java_fija = _ruta_java_launcher()
        if os.path.exists(ruta_java_fija):
            return ruta_java_fija

        # 3) Descargar
        if descargar_java_17():
            if os.path.exists(ruta_java_fija):
                return ruta_java_fija

        messagebox.showerror("Error de Java",
                             "No se encontró Java 17. Descárguelo desde https://adoptium.net o instálelo y reinicie el launcher.")
        return None

    except Exception as e:
        messagebox.showerror("Error", f"Problema al buscar Java: {e}")
        return None