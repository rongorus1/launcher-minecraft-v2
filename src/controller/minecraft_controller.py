import os
import platform
import subprocess
import time
import customtkinter as ctk
import logging
from tkinter import messagebox
import threading

import minecraft_launcher_lib

from components.progress_bar_generic import ProgressBarGeneric
from config import MINECRAFT_VERSION, FORGE_VERSION, MINECRAFT_DIRECTORY, SERVER_IP, SERVER_PORT, LAUNCHER_NAME
from helpers.java_tools import detectar_java
from helpers.preinstalled import buscar_juego_preinstalado, extraer_juego_preinstalado
from helpers.ram_tools import validate_ram
from services.logging_service import config_logging
from services.profile_service import load_profiles
from services.settings_service import load_settings


class MinecraftController:
    def __init__(self, root_window: ctk.CTk = None, progress_bar: ProgressBarGeneric = None):
        config_logging()
        self.logging = logging.getLogger()
        self.progress_bar = progress_bar
        self.root_window = root_window
        self.progress_bar_value_total: int = 0

    def _ui(self, func, *args):
        """Ejecuta una operacion de UI en el hilo principal (seguro desde hilos)."""
        if self.root_window is not None:
            try:
                self.root_window.after(0, lambda: func(*args))
            except Exception:
                pass

    def minecraft_set_status(self, text: str):
        self.logging.info(text)


    def minecraft_set_progress(self, value: int):
        if self.progress_bar:
            self._ui(self._aplicar_progreso, value)


    def _aplicar_progreso(self, value: int):
        if self.progress_bar is None:
            return
        if self.progress_bar.is_hidden:
            self.progress_bar.show_element()
        if self.progress_bar_value_total > 0 and value <= self.progress_bar_value_total:
            self.progress_bar.set(value / self.progress_bar_value_total)
        else:
            self.progress_bar.set(0.0)


    def minecraft_set_max(self, value: int):
        self.logging.info(value)
        self.progress_bar_value_total = value

    def _progreso_preinstalado(self, ratio: float):
        self._ui(self._aplicar_ratio, ratio)

    def _aplicar_ratio(self, ratio: float):
        if self.progress_bar is None:
            return
        if self.progress_bar.is_hidden:
            self.progress_bar.show_element()
        self.progress_bar.set(ratio)


    def _instalar_con_reintentos(self, nombre_fase: str, funcion, *args, **kwargs):
        """Ejecuta una fase de instalacion con reintentos.

        Si falla (timeout, conexion caida, checksum), reintenta. Como
        minecraft-launcher-lib salta los archivos ya descargados y correctos
        (verifica sha1), cada intento reanuda desde donde se quedo en lugar de
        empezar de cero.
        """
        intentos = 3
        for intento in range(1, intentos + 1):
            try:
                self.logging.info(f"Fase '{nombre_fase}': intento {intento}/{intentos}.")
                funcion(*args, **kwargs)
                self.logging.info(f"Fase '{nombre_fase}' completada.")
                return
            except Exception as e:
                self.logging.error(f"Fase '{nombre_fase}': error en el intento {intento}/{intentos}: {e}")
                if intento == intentos:
                    raise
                self.logging.info(
                    f"Fase '{nombre_fase}': se reintentara en 2 segundos (reanuda desde lo ya descargado).")
                time.sleep(2)


    def ejecutar_minecraft(self, window: ctk.CTkToplevel = None):
        def run_install():
            try:
                settings = load_settings()
                if not validate_ram(settings['ram']['min'], settings['ram']['max']):
                    self.root_window.after(0, lambda: messagebox.showerror("Error", "La RAM debe estar entre 4 y 16 GB"))
                    return

                java_path = detectar_java()
                if not java_path:
                    self.root_window.after(0, lambda: messagebox.showerror("Error", "No se pudo encontrar Java en el PATH"))
                    return

                forge_profile = f"{MINECRAFT_VERSION}-forge-{FORGE_VERSION}"

                data_profile = load_profiles()
                profile_names = [p['username'] for p in data_profile['profiles']]

                username = settings.get('last_profile')
                if not username or username not in profile_names:
                    username = profile_names[0] if profile_names else "Rongorus"

                options = {
                    "username": username,
                    "token": "",
                    "uuid": "",
                    "gameDirectory": MINECRAFT_DIRECTORY,
                    "java": java_path,
                    "jvmArguments": [f"-Xmx{settings['ram']['max']}", f"-Xms{settings['ram']['min']}"],
                    "launcherName": LAUNCHER_NAME,
                    "customResolution": False,
                    "launcherVersion": "1.0",
                    "server": SERVER_IP,
                    "port": SERVER_PORT,
                }

                forge_json = os.path.join(MINECRAFT_DIRECTORY, "versions", forge_profile, f"{forge_profile}.json")
                vanilla_json = os.path.join(MINECRAFT_DIRECTORY, "versions", MINECRAFT_VERSION, f"{MINECRAFT_VERSION}.json")

                callback = {'setStatus': self.minecraft_set_status, 'setProgress': self.minecraft_set_progress,
                            'setMax': self.minecraft_set_max}

                necesita_instalacion = not os.path.exists(forge_json) or not os.path.exists(vanilla_json)

                if necesita_instalacion:
                    self.logging.info("Minecraft/Forge no instalados o incompletos. Instalando...")
                    bundle = buscar_juego_preinstalado()
                    if bundle:
                        self.logging.info(f"Juego preinstalado encontrado: {bundle}. Copiando...")
                        self.root_window.after(0, lambda: messagebox.showinfo("Info", "Copiando juego preinstalado... no hace falta descargar."))
                        _top, err = extraer_juego_preinstalado(
                            bundle, MINECRAFT_DIRECTORY,
                            progress_callback=self._progreso_preinstalado)
                        if err:
                            self.logging.error(f"Error al copiar el juego preinstalado: {err}")
                        else:
                            self.logging.info("Juego preinstalado copiado correctamente.")
                    else:
                        self.root_window.after(0, lambda: messagebox.showinfo("Info", "Preparando Minecraft y Forge por primera vez. Esto puede tardar unos minutos..."))

                # Reparar/verificar Minecraft SIEMPRE antes de lanzar: descarga solo
                # lo que falta o esta corrupto (reanuda una instalacion interrumpida).
                self._instalar_con_reintentos(
                    "Minecraft",
                    minecraft_launcher_lib.install.install_minecraft_version,
                    MINECRAFT_VERSION, MINECRAFT_DIRECTORY, callback
                )

                if not os.path.exists(forge_json):
                    self._instalar_con_reintentos(
                        "Forge",
                        minecraft_launcher_lib.forge.install_forge_version,
                        f"{MINECRAFT_VERSION}-{FORGE_VERSION}", MINECRAFT_DIRECTORY, callback
                    )

                if not os.path.exists(forge_json):
                    raise RuntimeError("No se pudo instalar Forge. Revisa la conexión a internet y vuelve a intentarlo.")

                self.logging.info("Instalacion verificada y completa.")

                if self.progress_bar:
                    self._ui(self.progress_bar.hidde_element)

                command = minecraft_launcher_lib.command.get_minecraft_command(
                    forge_profile, MINECRAFT_DIRECTORY, options
                )

                self.logging.info(f"Iniciando Minecraft: {command}")

                if self.root_window is not None:
                    self.root_window.after(0, self.root_window.destroy)

                if platform.system() == "Windows":
                    subprocess.Popen(command, cwd=MINECRAFT_DIRECTORY, creationflags=subprocess.CREATE_NO_WINDOW)
                elif platform.system() == "Linux":
                    subprocess.Popen(command, cwd=MINECRAFT_DIRECTORY)
                else:  # macOS
                    subprocess.Popen(command, cwd=MINECRAFT_DIRECTORY)

            except Exception as e:
                self.logging.error(f"Error al iniciar Minecraft: {e}")
                self.root_window.after(0, lambda: messagebox.showerror("Error", f"No se pudo iniciar Minecraft: {e}"))
                if window is not None:
                    self.root_window.after(0, window.destroy)
                if self.root_window is not None:
                    self.root_window.after(0, self.root_window.destroy)

        threading.Thread(target=run_install, daemon=True).start()
