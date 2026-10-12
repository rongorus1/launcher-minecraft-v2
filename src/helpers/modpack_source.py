# src/helpers/modpack_source.py
"""Origen del modpack: último release publicado en GitHub.

El release debe traer un asset .zip con el export CurseForge
(manifest.json + overrides/). Los drafts NO los devuelve la API de
'releases/latest': hay que publicar el release.
"""
import logging
import os

import requests

logger = logging.getLogger(__name__)


def get_latest_modpack_asset(repo: str, asset_prefix: str):
    """Localiza el paquete del modpack en el último release publicado.

    Returns:
        (tag, asset, error): asset es el dict de la API de GitHub
        (name, browser_download_url, size). Si algo falla, asset es None
        y error trae el mensaje para la UI. Nunca lanza excepciones.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "RongonLang-Launcher",
                "Accept": "application/vnd.github+json",
            },
            timeout=(10, 20),
        )
    except Exception as e:
        logger.warning(f"No se pudo contactar a GitHub: {e}")
        return None, None, f"No se pudo contactar a GitHub: {e}"

    if r.status_code == 404:
        return None, None, (
            "Aún no hay un release publicado del modpack en GitHub "
            "(los borradores no cuentan)."
        )
    if r.status_code != 200:
        return None, None, (
            f"GitHub respondió {r.status_code} al buscar el modpack."
        )

    try:
        data = r.json()
    except Exception:
        return None, None, "Respuesta inválida de GitHub al buscar el modpack."

    tag = str(data.get("tag_name", "") or "")
    candidatos = [
        a for a in data.get("assets", [])
        if str(a.get("name", "")).startswith(asset_prefix)
    ]
    if not candidatos:
        return None, None, (
            f"El release {tag or 'actual'} no trae el paquete del modpack "
            f"(se busca '{asset_prefix}...')."
        )
    candidatos.sort(key=lambda a: str(a.get("name", "")), reverse=True)
    return tag, candidatos[0], None


def download_modpack(asset: dict, destino: str,
                     progress_callback: callable = None,
                     status_callback: callable = None) -> str:
    """Descarga el asset por streaming con progreso 0..1.

    Lanza RuntimeError/OSError con mensaje listo para la UI.
    No toca el juego: escribe solo en `destino`.
    """
    url = str(asset.get("browser_download_url", "") or "")
    nombre = str(asset.get("name", "modpack") or "modpack")
    if not url:
        raise RuntimeError("El asset no tiene URL de descarga.")

    total = int(asset.get("size") or 0)
    if status_callback is not None:
        status_callback(f"Descargando {nombre}...")

    try:
        r = requests.get(url, stream=True, timeout=(15, 300))
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"No se pudo descargar el modpack: {e}")

    if total <= 0:
        try:
            total = int(r.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            total = 0

    descargado = 0
    try:
        with open(destino, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                f.write(chunk)
                descargado += len(chunk)
                if progress_callback is not None and total > 0:
                    progress_callback(min(descargado / total, 1.0))
    except OSError as e:
        raise OSError(f"No se pudo guardar el modpack: {e}")

    if progress_callback is not None:
        progress_callback(1.0)
    return destino
