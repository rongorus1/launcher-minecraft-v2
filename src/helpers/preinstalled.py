import logging
import os
import shutil
import sys
import zipfile

from services.logging_service import config_logging

# Carpetas del juego preinstalado que se empaquetan y se copian
PREDIRECTOS = ("versions", "libraries", "assets", "runtime")

ZIP_NAME = "juego_preinstalado.zip"


def buscar_juego_preinstalado():
    """Devuelve la ruta al zip del juego preinstalado, o None si no existe.

    Busca junto al ejecutable, en la carpeta del paquete (una arriba del
    ejecutable), en el directorio actual y en la raiz del proyecto (dev).
    """
    candidatos = []
    try:
        exe_dir = os.path.dirname(sys.executable)
        candidatos.append(exe_dir)
        candidatos.append(os.path.dirname(exe_dir))
    except Exception:
        pass
    candidatos.append(os.getcwd())
    candidatos.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    vistos = set()
    for base in candidatos:
        if not base or base in vistos:
            continue
        vistos.add(base)
        ruta = os.path.join(base, ZIP_NAME)
        if os.path.isfile(ruta):
            return ruta
    return None


def _rel_segura(member):
    """Normaliza un miembro del zip y neutraliza path traversal."""
    rel = member.replace("\\", "/")
    partes = []
    for parte in rel.split("/"):
        if parte in ("", "."):
            continue
        if parte == "..":
            partes.append("_")
            continue
        partes.append(parte)
    return os.path.join(*partes)


def extraer_juego_preinstalado(zip_path: str, minecraft_dir: str,
                               progress_callback: callable = None):
    """Copia el juego preinstalado del zip al .minecraft.

    Solo extrae versions/, libraries/, assets/ y runtime/. Salta los archivos
    que ya existen con el mismo tamano (reanuda una copia cortada). La
    verificacion real de cada archivo la hace install_minecraft_version al
    lanzar, asi que una copia imperfecta se auto-repara.

    Devuelve (carpetas, error): carpetas = {"versions", "libraries", ...} o
    None si fallo, error = mensaje o None.
    """
    config_logging()
    logger = logging.getLogger()

    if not os.path.isfile(zip_path):
        return None, f"El archivo no existe: {zip_path}"

    try:
        opener = zipfile.ZipFile(zip_path)
        miembros = opener.infolist()
    except Exception as e:
        logger.error(f"No se pudo abrir el zip preinstalado: {e}")
        return None, f"No se pudo abrir el zip preinstalado: {e}"

    total_bytes = sum(
        m.file_size for m in miembros
        if not m.is_dir() and _rel_segura(m.filename).split(os.sep)[0] in PREDIRECTOS
    )
    if total_bytes == 0:
        return None, "El zip preinstalado esta vacio o incompleto."

    hechos = 0
    for m in miembros:
        if m.is_dir():
            continue
        rel = _rel_segura(m.filename)
        if not rel or rel.split(os.sep)[0] not in PREDIRECTOS:
            continue

        destino = os.path.join(minecraft_dir, rel)

        if os.path.isfile(destino) and os.path.getsize(destino) == m.file_size:
            hechos += m.file_size
            if progress_callback is not None:
                progress_callback(min(hechos / total_bytes, 1.0))
            continue

        try:
            padre = os.path.dirname(destino)
            if padre:
                os.makedirs(padre, exist_ok=True)
            with opener.open(m) as src, open(destino, "wb") as dst:
                shutil.copyfileobj(src, dst)
        except Exception as e:
            logger.warning(f"Se omitio {m.filename}: {e}")

        hechos += m.file_size
        if progress_callback is not None:
            progress_callback(min(hechos / total_bytes, 1.0))

    return set(PREDIRECTOS), None