from tkinter import messagebox

import customtkinter as ctk

from components.button_save import ButtonSave
from components.progress_bar_generic import ProgressBarGeneric
from controller.minecraft_controller import MinecraftController
from services.settings_service import load_settings, save_settings


class RamConfigurationWindow(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk = None, progress_bar: ProgressBarGeneric = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Configuración de RAM para Minecraft")
        self.geometry("400x300")
        self.attributes('-topmost', True)

        ctk.CTkLabel(self, text="Configuración de RAM", font=("Arial", 16)).pack(pady=10)

        settings = load_settings()
        # Valor inicial: RAM máxima guardada (por defecto 8 GB)
        try:
            valor_inicial = int(str(settings['ram']['max']).replace('G', ''))
        except (KeyError, ValueError):
            valor_inicial = 8
        if valor_inicial < 4 or valor_inicial > 16:
            valor_inicial = 8

        ram_var = ctk.IntVar(value=valor_inicial)

        ctk.CTkLabel(self, text="RAM para Minecraft (GB):").pack(pady=5)
        ram_label = ctk.CTkLabel(self, text=f"{valor_inicial} GB", font=("Arial", 14))
        ram_label.pack(pady=5)

        ram_slider = ctk.CTkSlider(self, from_=4, to=16, number_of_steps=12, variable=ram_var)
        ram_slider.pack(pady=10, padx=30, fill="x")

        def actualizar_label(_=None):
            ram_label.configure(text=f"{ram_var.get()} GB")

        ram_slider.configure(command=actualizar_label)

        def guardar_y_ejecutar():
            ram_numerica = ram_var.get()

            # Validaciones de RAM
            if ram_numerica < 4 or ram_numerica > 16:
                messagebox.showerror("Error", "La RAM debe estar entre 4 y 16 GB")
                return

            # Guardar configuración
            settings['ram']['min'] = f"{ram_numerica // 2}G"  # La mitad como RAM mínima
            settings['ram']['max'] = f"{ram_numerica}G"
            save_settings(settings)

            # Cerrar ventana y ejecutar Minecraft
            self.destroy()
            minecraft_controller = MinecraftController(root_window=None if master is None else master, progress_bar=progress_bar)
            minecraft_controller.ejecutar_minecraft(self)

        button_save = ButtonSave(self, command=guardar_y_ejecutar)
        button_save.pack(pady=10)