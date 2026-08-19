from __future__ import annotations

import tkinter.filedialog as fd


def select_file_archive() -> str | None:
    file_path = fd.askopenfilename(
        title="Seleccionar modpack (.rar o .zip)",
        filetypes=[("Modpack", "*.rar *.zip"), ("Archivos RAR", "*.rar"), ("Archivos ZIP", "*.zip")],
        initialdir="."
    )

    if file_path:
        return file_path

    return None