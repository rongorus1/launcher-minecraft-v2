# src/helpers/config_curseforge.py
"""Configuración para CurseForge API."""
import os
import json
from pathlib import Path

# Rutas candidatas del config local (orden de prioridad).
# NOTA: estos archivos están en .gitignore, nunca se suben a GitHub.
# Se distribuye solo curseforge_config.json.example como plantilla.
def _candidate_config_paths():
    here = Path(__file__).resolve()
    root = here.parent.parent.parent  # raíz del repo
    src_dir = here.parent.parent      # src/
    return [
        root / "curseforge_config.json",
        src_dir / "curseforge_config.json",  # compat: tu key actual vive aquí
    ]

# Configuración de CurseForge API (carga inicial, solo local)
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY", "")

# Si no está en variable de entorno, buscar en archivo de configuración local
if not CURSEFORGE_API_KEY:
    for _p in _candidate_config_paths():
        if _p.exists():
            try:
                with open(_p, 'r') as f:
                    CURSEFORGE_API_KEY = json.load(f).get("api_key", "")
                if CURSEFORGE_API_KEY:
                    break
            except Exception:
                continue

# Variable global que se actualiza dinámicamente
_API_KEY = CURSEFORGE_API_KEY

def get_api_key() -> str:
    """Obtiene la API key configurada (revisa env y config file cada vez)."""
    # 1. Variable de entorno (prioridad máxima, útil en CI)
    env_key = os.getenv("CURSEFORGE_API_KEY")
    if env_key:
        return env_key

    # 2. Archivos de config local (solo en tu PC, ignorados por git)
    for config_path in _candidate_config_paths():
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    key = json.load(f).get("api_key", "")
                    if key:
                        return key
            except Exception:
                continue
    return ""

def validate_api_key() -> bool:
    """Verifica si la API key está configurada."""
    return bool(get_api_key())

def set_api_key(api_key: str) -> None:
    """Guarda la API key en archivo de configuración local."""
    import json
    config_path = Path(__file__).parent.parent.parent / "curseforge_config.json"
    config = {"api_key": api_key}
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"API Key guardada en {config_path}")