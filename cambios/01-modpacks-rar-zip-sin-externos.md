# 01 · Modpacks RAR/ZIP sin programas externos

## Qué cambió
- Nuevo `src/helpers/archive_tools.py` basado en **unrar2-cffi** (incluye la librería dentro del ejecutable; el jugador NO necesita instalar `unrar`).
- Se eliminó `src/helpers/rar_tools.py` (dependía de `rarfile` + binario externo).
- `src/controller/update_mods_controller.py` ahora usa `archive_tools.extract_modpack`.
- `src/requirements.txt`: añadido `unrar2-cffi`.

## Comportamiento de extracción
- Se quita la carpeta envolvente automáticamente.
- `mods/`, `config/`, `kubejs/`, `scripts/`, etc. se colocan directamente dentro de `.minecraft`.
- Los jars sueltos van a `mods/`.
- La carpeta `mods/` solo se reemplaza si el modpack trae mods.