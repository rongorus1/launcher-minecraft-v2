import customtkinter as ctk
import os
import sys
import threading
import tempfile
import logging
from tkinter import messagebox
from PIL import Image, ImageTk

from components.button_login import ButtonLogin
from components.button_play import ButtonPlay
from components.button_ram_setting import ButtonRamSetting
from components.button_update_mods import ButtonUpdateMods
from components.progress_bar_generic import ProgressBarGeneric
from config import LAUNCHER_NAME
from controller.ram_window_controller import open_window_configurar_ram
from controller.start_session_controller import run_session_controller
from controller.update_mods_controller import run_update_mods_controller
from version import VERSION, GITHUB_REPO
from helpers.updater import version_remota, descargar_actualizacion, aplicar_actualizacion, lanzar_actualizacion, _es_version_superior


class MainWindow(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.progressbar: ProgressBarGeneric = None
        self.update_mods_button = None
        self.login_button = None
        self.ram_settings_button = None
        self.play_button = None

        self.title(LAUNCHER_NAME)
        self.geometry("1200x700")

        self.bg_image = None
        self.bg_label = None

        # Load and set background image
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        if os.path.exists(assets_path):
            bg_image_path = os.path.join(assets_path, 'background.png')
            if os.path.exists(bg_image_path):
                self.bg_image = ctk.CTkImage(
                    light_image=Image.open(bg_image_path),
                    dark_image=Image.open(bg_image_path),
                    size=(1200, 700)
                )
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.bind("<Configure>", self.resize_bg)

        # Load components
        self.load_components()

        # Revisar actualizaciones en segundo plano (solo en el exe compilado)
        if getattr(sys, "frozen", False):
            threading.Thread(target=self._revisar_actualizacion, daemon=True).start()

    def _revisar_actualizacion(self):
        try:
            nueva, asset = version_remota(GITHUB_REPO)
            if not nueva or not asset or not _es_version_superior(nueva, VERSION):
                return
            self.after(0, lambda: self._preguntar_actualizacion(nueva, asset))
        except Exception as e:
            logging.getLogger().warning(f"No se pudo revisar actualizaciones: {e}")

    def _preguntar_actualizacion(self, nueva, asset):
        if messagebox.askyesno(
                LAUNCHER_NAME,
                f"Hay una nueva versión disponible ({nueva}).\n"
                "¿Actualizar ahora? Se reiniciará el launcher automáticamente."):
            threading.Thread(target=lambda: self._aplicar_actualizacion(asset), daemon=True).start()

    def _aplicar_actualizacion(self, asset):
        try:
            tmp = os.path.join(tempfile.gettempdir(), "rongonlang_update.zip")
            if os.path.exists(tmp):
                os.remove(tmp)
            descargar_actualizacion(asset, tmp)
            bat = aplicar_actualizacion(tmp)
            if os.path.exists(tmp):
                os.remove(tmp)
            lanzar_actualizacion(bat)
            self.after(0, self.destroy)
        except Exception as e:
            logging.getLogger().error(f"Error al actualizar: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"No se pudo actualizar: {e}"))

    # Add components
    def load_components(self):

        self.progressbar = ProgressBarGeneric(self)

        self.play_button = ButtonPlay(
            self,
            command=lambda: open_window_configurar_ram(master=self, progressbar = self.progressbar),
            is_center=True
        )
        self.login_button = ButtonLogin(
            self,
            command=lambda: run_session_controller(master=self),
            relx=0.05,
            rely=0.05
        )
        self.ram_settings_button = ButtonRamSetting(
            self,
            command=lambda: open_window_configurar_ram(master=self, progressbar = self.progressbar),
            relx=0.05,
            rely=0.15
        )

        self.update_mods_button = ButtonUpdateMods(
            self,
            command = lambda: run_update_mods_controller(self.progressbar),
            relx=0.05,
            rely=0.25
        )

    def resize_bg(self, event):
        if self.bg_image is not None:
            self.bg_image._size = (event.width, event.height)
            self.bg_label.configure(image=self.bg_image)

        if self.progressbar is not None:
            self.progressbar.update_width(event.width)


    def run(self):
        self.mainloop()

    def close(self):
        self.destroy()