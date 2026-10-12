# src/helpers/__init__.py
"""Helpers package for RongonLang Launcher."""
from .curseforge_api import CurseForgeAPI
from .manifest_parser import ManifestParser, ModDependency
from .curseforge_downloader import CurseForgeDownloader

# Lazy imports for config_curseforge (requires API key to be set first)
def get_api_key():
    from .config_curseforge import get_api_key as _get_api_key
    return _get_api_key()

def validate_api_key():
    from .config_curseforge import validate_api_key as _validate_api_key
    return _validate_api_key()

def set_api_key(api_key: str):
    from .config_curseforge import set_api_key as _set_api_key
    return _set_api_key(api_key)

__all__ = [
    "CurseForgeAPI",
    "ManifestParser",
    "ModDependency",
    "CurseForgeDownloader",
    "get_api_key",
    "validate_api_key",
    "set_api_key",
]