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
from helpers.java_tools import java_ya_instalada, descargar_java_17
from helpers.preinstalled import buscar_juego_preinstalado, extraer_juego_preinstalado
from helpers.ram_tools import validate_ram
from helpers.robust_network import obtener_velocidad_ultima_mbps
from services.logging_service import config_logging
from services.profile_service import load_profiles
from services.settings_service import load_settings

# Traduccion de los estados que manda minecraft-launcher-lib (son en ingles)
_TRADUCCIONES_ESTADO = {
    "Download Libraries": "Descargando librerías",
    "Download Assets": "Descargando assets",
    "Install java runtime": "Instalando Java (runtime de Mojang)",
    "Installation complete": "Instalación completa",
}


def _traducir_estado(texto: str) -> str:
    if texto in _TRADUCCIONES_ESTADO:
        return _TRADUCCIONES_ESTADO[texto]
    if texto.startswith("Running processor "):
        return "Aplicando Forge: " + texto[len("Running processor "):]
    if texto.startswith("Download "):
        return "Descargando " + texto[len("Download "):]
    return texto


class MinecraftController:
    def __init__(self, root_window: ctk.CTk = None, progress_bar: ProgressBarGeneric = None):
        config_logging()
        self.logging = logging.getLogger()
        self.progress_bar = progress_bar
        self.root_window = root_window
        self.progress_bar_value_total: int = 0
        self.estado_actual: str = ""
        self.estado_progreso: int = 0
        self.max_actual: int = 0

    def _ui(self, func, *args):
        """Ejecuta una operacion de UI en el hilo principal (seguro desde hilos)."""
        if self.root_window is not None:
            try:
                self.root_window.after(0, lambda: func(*args))
            except Exception:
                pass

    def minecraft_set_status(self, text: str):
        estado = _traducir_estado(text)
        self.estado_actual = estado
        self.logging.info(f"[Fase] {estado}")
        self._actualizar_estado_ui()

    def _actualizar_estado_ui(self):
        if self.progress_bar is None:
            return
        texto = self.estado_actual
        if self.max_actual > 0:
            texto += f" · {self.estado_progreso}/{self.max_actual}"
        velocidad = obtener_velocidad_ultima_mbps()
        if velocidad > 0:
            texto += f" · {velocidad:.1f} MB/s"
        self._ui(self.progress_bar.set_status_thread_safe, texto)

    def minecraft_set_progress(self, value: int):
        self.estado_progreso = value
        self._actualizar_estado_ui()
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
        self.max_actual = value
        self.estado_progreso = 0
        if value > 0:
            self.progress_bar_value_total = value

    def _progreso_preinstalado(self, ratio: float):
        self._ui(self._aplicar_ratio, ratio)

    def _estado_preinstalado(self, rel: str):
        if self.progress_bar is not None:
            self._ui(self.progress_bar.set_status_thread_safe, f"Copiando juego preinstalado: {rel}")

    def _aplicar_ratio(self, ratio: float):
        if self.progress_bar is None:
            return
        if self.progress_bar.is_hidden:
            self.progress_bar.show_element()
        self.progress_bar.set(ratio)


    def _descargar_java_hilo(self, resultado: dict):
        """Descarga Java 17 en segundo plano (en paralelo con las librerias)."""
        try:
            from helpers.java_tools import ruta_java_launcher
            ok = descargar_java_17(
                progress_callback=self._progreso_java,
                status_callback=self._estado_java,
                silencioso=True)
            if ok and ruta_java_launcher():
                resultado['path'] = ruta_java_launcher()
                self.logging.info(f"[Fase] Java 17 instalado en paralelo: {ruta_java_launcher()}")
            else:
                resultado['error'] = "No se pudo instalar Java 17 automaticamente. Descargalo desde https://adoptium.net e intentalo de nuevo."
        except Exception as e:
            self.logging.error(f"Error instalando Java en paralelo: {e}")
            resultado['error'] = f"No se pudo instalar Java 17: {e}"

    def _progreso_java(self, ratio: float):
        self._ui(self._aplicar_ratio, ratio)

    def _estado_java(self, texto: str):
        if self.progress_bar is not None:
            self._ui(self.progress_bar.set_status_thread_safe, texto)


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
                self.logging.info(f"[Fase] {nombre_fase}: intento {intento}/{intentos}.")
                funcion(*args, **kwargs)
                self.logging.info(f"[Fase] {nombre_fase} completada.")
                return
            except Exception as e:
                self.logging.error(f"[Fase] {nombre_fase}: error en el intento {intento}/{intentos}: {e}")
                if intento == intentos:
                    raise
                self.logging.info(
                    f"[Fase] {nombre_fase}: se reintentara en 2 segundos (reanuda desde lo ya descargado).")
                time.sleep(2)


    def ejecutar_minecraft(self, window: ctk.CTkToplevel = None):
        def run_install():
            try:
                settings = load_settings()
                if not validate_ram(settings['ram']['min'], settings['ram']['max']):
                    self.root_window.after(0, lambda: messagebox.showerror("Error", "La RAM debe estar entre 4 y 16 GB"))
                    return

                # --- Java: si no esta instalado se descarga EN PARALELO con las
                #     librerias de Minecraft (antes era secuencial) ---
                self.logging.info("[Fase] Buscando Java 17...")
                java_path = java_ya_instalada()
                hilo_java = None
                resultado_java = {'path': java_path, 'error': None}
                if java_path is None:
                    self.logging.info("[Fase] Java no encontrado: se descargara en paralelo con las librerias.")
                    resultado_java = {'path': None, 'error': None}
                    hilo_java = threading.Thread(
                        target=self._descargar_java_hilo, args=(resultado_java,), daemon=True)
                    hilo_java.start()
                else:
                    self.logging.info(f"[Fase] Java detectado: {java_path}")

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
                    "java": java_path if java_path else "",
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
                        self.logging.info(f"[Fase] Copiando juego preinstalado: {bundle}")
                        self.root_window.after(0, lambda: messagebox.showinfo("Info", "Copiando juego preinstalado... no hace falta descargar."))
                        _top, err = extraer_juego_preinstalado(
                            bundle, MINECRAFT_DIRECTORY,
                            progress_callback=self._progreso_preinstalado,
                            status_callback=self._estado_preinstalado)
                        if err:
                            self.logging.error(f"Error al copiar el juego preinstalado: {err}")
                        else:
                            self.logging.info("Juego preinstalado copiado correctamente.")
                    else:
                        self.root_window.after(0, lambda: messagebox.showinfo("Info", "Preparando Minecraft y Forge por primera vez. Esto puede tardar unos minutos..."))

                # Reparar/verificar Minecraft SIEMPRE antes de lanzar: descarga solo
                # lo que falta o esta corrupto (reanuda una instalacion interrumpida).
                # Corre en paralelo con la descarga de Java.
                self.logging.info("[Fase] Minecraft: verificando/descargando librerias, assets y jar")
                self._instalar_con_reintentos(
                    "Minecraft",
                    minecraft_launcher_lib.install.install_minecraft_version,
                    MINECRAFT_VERSION, MINECRAFT_DIRECTORY, callback
                )

                # Forge necesita Java para sus procesadores: esperar a que termine.
                if hilo_java is not None:
                    hilo_java.join()
                java_path = resultado_java['path']
                if not java_path:
                    self.logging.error(f"Error de Java: {resultado_java['error']}")
                    self.root_window.after(0, lambda: messagebox.showerror(
                        "Error de Java",
                        resultado_java['error'] or "No se pudo instalar Java 17. Descárguelo desde https://adoptium.net e intente de nuevo."))
                    return

                if not os.path.exists(forge_json):
                    self.logging.info("[Fase] Forge: instalando procesadores y verificando")
                    self._instalar_con_reintentos(
                        "Forge",
                        minecraft_launcher_lib.forge.install_forge_version,
                        f"{MINECRAFT_VERSION}-{FORGE_VERSION}", MINECRAFT_DIRECTORY, callback,
                        java=java_path
                    )

                if not os.path.exists(forge_json):
                    raise RuntimeError("No se pudo instalar Forge. Revisa la conexión a internet y vuelve a intentarlo.")

                self.logging.info("Instalacion verificada y completa.")

                options["java"] = java_path

                if self.progress_bar:
                    self._ui(self.progress_bar.hidde_element)

                command = minecraft_launcher_lib.command.get_minecraft_command(
                    forge_profile, MINECRAFT_DIRECTORY, options
                )

                self.logging.info(f"[Fase] Lanzando Minecraft: {command}")

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
