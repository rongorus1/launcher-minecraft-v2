import os
import platform
import re
import shutil
import subprocess
import tarfile
import zipfile
from tkinter import messagebox
import logging

import requests

from config import LAUNCHER_DIR


def _ruta_java_launcher():
    return os.path.join(LAUNCHER_DIR, "Java", "java17", "bin", "java.exe" if platform.system() == "Windows" else "java")


def ruta_java_launcher():
    """Ruta donde el launcher instala su propio Java 17 (este o no instalado)."""
    return _ruta_java_launcher()


def java_ya_instalada():
    """Devuelve la ruta de Java 17+ si ya existe (PATH o la del launcher), o None.

    No descarga nada: es la comprobacion rapida para saber si hace falta
    descargar Java en paralelo con las librerias.
    """
    ruta = _java_en_path()
    if ruta:
        return ruta
    ruta_fija = _ruta_java_launcher()
    if os.path.exists(ruta_fija):
        return ruta_fija
    return None


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


def descargar_java_17(progress_callback: callable = None,
                      status_callback: callable = None,
                      silencioso: bool = False):
    """Descargar e instalar Temurin 17 (JRE) en la carpeta del launcher.

    No requiere herramientas externas: zip para Windows, tar.gz para macOS/Linux.
    Con `silencioso=True` no muestra messageboxes (para descargar en paralelo,
    donde el progreso se muestra en la barra del launcher). Con
    `progress_callback`/`status_callback` informa avance (0..1) y texto.
    """
    def _reportar(texto=None, ratio=None):
        if status_callback is not None and texto is not None:
            status_callback(texto)
        if progress_callback is not None and ratio is not None:
            progress_callback(ratio)

    def _informar_ok(texto):
        if not silencioso:
            messagebox.showinfo("Éxito", texto)

    def _informar_error(texto):
        if not silencioso:
            messagebox.showerror("Error", texto)

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

        if not silencioso:
            messagebox.showinfo("Instalación de Java", "Descargando Java 17. Esto puede tardar unos minutos...")

        ruta_descarga = os.path.join(java_dir, "java17_tmp")
        temp_dir = os.path.join(java_dir, "java17_tmp_dir")

        # 3 intentos por si la conexion se corta (timeout global aplicado)
        for intento in range(1, 4):
            try:
                _reportar(texto=f"Descargando Java 17 (intento {intento}/3)...")
                respuesta = requests.get(java_url, stream=True, allow_redirects=True, timeout=60)
                respuesta.raise_for_status()
                total = int(respuesta.headers.get("content-length") or 0)
                descargados = 0
                with open(ruta_descarga, 'wb') as archivo:
                    for fragmento in respuesta.iter_content(chunk_size=8192):
                        if not fragmento:
                            continue
                        archivo.write(fragmento)
                        descargados += len(fragmento)
                        if total > 0:
                            _reportar(
                                texto=f"Descargando Java 17 ({descargados // (1024 * 1024)}/{total // (1024 * 1024)} MB)",
                                ratio=min(descargados / total, 1.0))
                break
            except Exception as e:
                logging.getLogger().warning(f"Descarga de Java fallida ({intento}/3): {e}")
                if intento == 3:
                    _informar_error(f"No se pudo descargar Java: {e}")
                    return False

        # Extraer a un directorio temporal para luego dejar solo java17/
        _reportar(texto="Descomprimiendo Java 17...", ratio=None)
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
            _informar_ok("Java 17 se ha instalado correctamente")
            return True

        _informar_error("No se pudo instalar Java automáticamente")
        return False

    except Exception as e:
        _informar_error(f"No se pudo instalar Java: {e}")
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