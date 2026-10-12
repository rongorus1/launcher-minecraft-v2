import re


def validate_ram(min_ram, max_ram):
    """Valida RAM ("4G"/"8G"). Pura y sin UI: segura en hilos.

    Regla (sin cambios): min >= 1, max <= 16 y min < max.
    El llamador muestra el mensaje (ver minecraft_controller).
    """
    try:
        min_val = int(re.findall(r'\d+', min_ram)[0])
        max_val = int(re.findall(r'\d+', max_ram)[0])
    except Exception:
        return False

    if min_val < 1 or max_val > 16:
        return False

    if min_val >= max_val:
        return False

    return True