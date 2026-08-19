import logging
import os
import shutil
import zipfile

from components.progress_bar_generic import ProgressBarGeneric
from services.logging_service import config_logging

# Folders that a modpack may contain and that map directly inside .minecraft
MC_DIRS = {
    "mods", "config", "kubejs", "defaultconfigs", "scripts", "shaderpacks",
    "resourcepacks", "datapacks", "global_packs", "plugins", "saves", "local",
    "crash-reports", "logs", "serverconfigs", "patchouli_books",
    "fancymenu_data",
}


def is_rar(path):
    return path.lower().endswith(".rar")


def is_zip(path):
    return path.lower().endswith(".zip")


def _detect_layout(files):
    """Decide how the archive contents should be mapped into .minecraft.

    Returns (strip_prefix, flat):
      - strip_prefix: a leading folder to remove (wrapping folder like "Modpack/")
      - flat: True when the archive has loose files at its root, which must
              be placed into the "mods" folder
    """
    tops = set()
    has_dir = False
    for f in files:
        f = f.replace("\\", "/")
        if "/" in f:
            has_dir = True
            tops.add(f.split("/", 1)[0])
        else:
            tops.add(f)

    # Everything inside a single wrapping folder that is not an MC folder
    if has_dir and len(tops) == 1:
        top = next(iter(tops))
        if top not in MC_DIRS:
            return top + "/", False

    # Loose files at the root (e.g. just .jar mods)
    if not has_dir:
        return "", True

    return "", False


def _safe_relative(rel):
    """Normalise a member path and neutralise any path traversal."""
    rel = rel.replace("\\", "/")
    parts = []
    for part in rel.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            parts.append("_")
            continue
        parts.append(part)
    return os.path.join(*parts)


def extract_modpack(archive_path: str, minecraft_dir: str,
                    progress_bar: ProgressBarGeneric = None,
                    progress_callback: callable = None,
                    status_callback: callable = None):
    """Extract a .rar/.zip modpack straight into the .minecraft directory.

    Returns (top_folders, error_message): top_folders is the set of folders
    written (e.g. {"mods", "config"}), error_message is None on success.

    progress_callback (optional) receives a ratio in [0, 1] and is called from
    the calling thread; prefer it over progress_bar for background threads.
    status_callback (optional) receives the current file/folder being
    extracted, para mostrarlo en la UI.
    """
    config_logging()
    logger = logging.getLogger()

    if not os.path.isfile(archive_path):
        return None, f"El archivo no existe: {archive_path}"

    try:
        if is_rar(archive_path):
            from unrar.cffi import rarfile
            opener = rarfile.RarFile(archive_path)
            infos = opener.infolist()
            read_fn = opener.read

            def _es_directorio(info):
                # En los modpacks RAR el flag de directorio puede venir mal
                # puesto: un directorio real siempre pesa 0 bytes.
                return bool(getattr(info, "is_dir", False)) and info.file_size == 0
        elif is_zip(archive_path):
            opener = zipfile.ZipFile(archive_path)
            infos = opener.infolist()
            read_fn = opener.read

            def _es_directorio(info):
                return info.is_dir()
        else:
            return None, "El archivo debe ser .rar o .zip"
    except Exception as e:
        logger.error(f"No se pudo abrir el archivo: {e}")
        return None, f"No se pudo abrir el archivo: {e}"

    def _nombre(info):
        return info.filename.replace("\\", "/")

    archivos = [i for i in infos if not _es_directorio(i) and not _nombre(i).endswith(("/", "\\"))]
    directorios = [i for i in infos if _es_directorio(i)]
    if not archivos:
        return None, "El archivo no contiene archivos"

    strip_prefix, flat = _detect_layout([_nombre(i) for i in archivos])

    targets = []
    for info in archivos:
        rel = _nombre(info)
        if strip_prefix and rel.startswith(strip_prefix):
            rel = rel[len(strip_prefix):]
        rel = rel.lstrip("/")
        if flat:
            rel = os.path.join("mods", os.path.basename(rel))
        targets.append((info.filename, _safe_relative(rel)))

    top_folders = set()
    for _, rel in targets:
        top = rel.split(os.sep)[0] if os.sep in rel else rel
        if top:
            top_folders.add(top)

    # Las carpetas vacias que declare el modpack se crean como carpetas reales
    # (p.ej. las de fancymenu_data); antes se escribian como archivos de 0
    # bytes y mods como FancyMenu fallaban al crearlas.
    if not flat:
        for info in directorios:
            rel = _nombre(info)
            if strip_prefix and rel.startswith(strip_prefix):
                rel = rel[len(strip_prefix):]
            rel = rel.lstrip("/")
            safe = _safe_relative(rel)
            if not safe:
                continue
            if status_callback is not None:
                status_callback(f"Creando carpeta {rel}/...")
            try:
                os.makedirs(os.path.join(minecraft_dir, safe), exist_ok=True)
            except OSError as e:
                logger.warning(f"No se pudo crear la carpeta {rel}: {e}")

    # Only replace the mods folder when the pack actually provides mods
    if flat or "mods" in top_folders:
        mods_dir = os.path.join(minecraft_dir, "mods")
        if status_callback is not None:
            status_callback("Reemplazando carpeta mods/...")
        if os.path.isdir(mods_dir):
            shutil.rmtree(mods_dir)
        os.makedirs(mods_dir, exist_ok=True)

    total = len(targets)
    for idx, (name, rel) in enumerate(targets, 1):
        if not rel:
            continue
        target = os.path.join(minecraft_dir, rel)

        if status_callback is not None:
            status_callback(f"Extrayendo {rel} ({idx}/{total})")

        try:
            data = read_fn(name)
        except Exception as e:
            logger.warning(f"Se omitió {name} (no se pudo leer): {e}")
            continue

        # A file that already exists as a directory (name collision inside
        # the archive) is skipped instead of aborting the whole extraction.
        if os.path.isdir(target):
            logger.warning(f"Se omitió {name} (colisión con un directorio)")
            continue

        parent = os.path.dirname(target)
        if parent:
            try:
                os.makedirs(parent, exist_ok=True)
            except OSError as e:
                logger.warning(f"Se omitió {name} (no se pudo crear su carpeta): {e}")
                continue

        try:
            with open(target, "wb") as fh:
                fh.write(data)
        except OSError as e:
            logger.warning(f"Se omitió {name}: {e}")
            continue

        if progress_callback is not None:
            progress_callback(idx / total)
        elif progress_bar is not None:
            if progress_bar.is_hidden:
                progress_bar.show_element()
            progress_bar.set(idx / total)
            progress_bar.update_idletasks()

    return top_folders, None