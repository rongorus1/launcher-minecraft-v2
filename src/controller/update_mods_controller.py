import threading
from tkinter import messagebox

from components.progress_bar_generic import ProgressBarGeneric
from config import MINECRAFT_DIRECTORY
from helpers.archive_tools import extract_modpack
from helpers.file_dialog_tools import select_file_archive


def run_update_mods_controller(progress_bar: ProgressBarGeneric = None):
    archive_path = select_file_archive()

    if not archive_path:
        return

    def instalar():
        def reportar_progreso(ratio):
            if progress_bar is not None:
                progress_bar.show_element_thread_safe()
                progress_bar.set_thread_safe(ratio)

        top_folders, error = extract_modpack(archive_path, MINECRAFT_DIRECTORY, progress_callback=reportar_progreso)

        master = progress_bar.master if progress_bar is not None else None

        if progress_bar is not None:
            progress_bar.hidde_element_thread_safe()

        if error:
            if master is not None:
                master.after(0, lambda: messagebox.showerror("Error", error))
            return

        if master is not None:
            master.after(0, lambda: messagebox.showinfo(
                "Modpack instalado", "Los mods y carpetas del modpack se instalaron correctamente"))

    threading.Thread(target=instalar, daemon=True).start()