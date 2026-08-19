import re
from tkinter import messagebox


def validate_ram(min_ram, max_ram):
    """Validate RAM settings. min_ram/max_ram come as strings like "4G"."""
    try:
        min_val = int(re.findall(r'\d+', min_ram)[0])
        max_val = int(re.findall(r'\d+', max_ram)[0])

        if min_val < 1 or max_val > 16:
            raise ValueError("La RAM máxima debe estar entre 4 y 16 GB")

        if min_val >= max_val:
            raise ValueError("La RAM mínima debe ser menor que la máxima")

        return True
    except Exception as e:
        messagebox.showerror("Error de configuración de RAM", str(e))
        return False