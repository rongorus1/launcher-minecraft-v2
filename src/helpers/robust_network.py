import logging
import os
import threading
import time

import requests
import minecraft_launcher_lib._helper

_CONNECT_TIMEOUT = 15
_READ_TIMEOUT = 120
DESCARGAS_REINTENTOS = 3

_velocidad_lock = threading.Lock()
_velocidad_ultima_mbps = 0.0


def obtener_velocidad_ultima_mbps() -> float:
    """Velocidad (MB/s) de la ultima descarga completada, para mostrarla en la UI."""
    with _velocidad_lock:
        return _velocidad_ultima_mbps


def _registrar_velocidad(mbps: float):
    global _velocidad_ultima_mbps
    with _velocidad_lock:
        _velocidad_ultima_mbps = mbps


def _aplicar_timeout_global():
    """Inyecta un timeout (connect, read) a TODAS las requests del proceso.

    minecraft-launcher-lib llama requests.get/session.get sin timeout, y si la
    conexion deja de responder el hilo se queda colgado para siempre (bug de la
    instalacion que quedo toda la noche en 66%). Con timeout la lectura del
    socket se aborta y se puede reintentar.
    """
    original_request = requests.sessions.Session.request

    def request_con_timeout(self, method, url, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = (_CONNECT_TIMEOUT, _READ_TIMEOUT)
        return original_request(self, method, url, **kwargs)

    requests.sessions.Session.request = request_con_timeout


def _aplicar_reintentos_descarga():
    """Reintenta cada descarga de minecraft-launcher-lib (se reanuda sola).

    install.install_libraries se traga los errores por libreria (except: pass),
    asi que una libreria que falla una vez queda omitida silenciosamente. Con
    reintentos por archivo, una conexion cortada se vuelve a intentar y el
    archivo se baja completo (se reanuda porque ya tiene el sha1 bueno).
    """
    def _wrap(module):
        original = module.download_file
        logger = logging.getLogger()

        def retry_download(url, path, callback={}, sha1=None, lzma_compressed=False,
                           session=None, minecraft_directory=None, overwrite=False):
            last_error = None
            for intento in range(1, DESCARGAS_REINTENTOS + 1):
                inicio = time.monotonic()
                try:
                    resultado = original(url, path, callback, sha1, lzma_compressed,
                                         session, minecraft_directory, overwrite)
                    transcurrido = time.monotonic() - inicio
                    if resultado is True and transcurrido >= 0.1:
                        try:
                            tamano_mb = os.path.getsize(path) / (1024 * 1024)
                            mbps = tamano_mb / transcurrido
                            _registrar_velocidad(mbps)
                            logger.info(
                                f"Descargado {os.path.basename(path)}: {tamano_mb:.1f} MB ({mbps:.1f} MB/s)")
                        except OSError:
                            pass
                    return resultado
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Descarga fallida ({intento}/{DESCARGAS_REINTENTOS}): {e}")
            raise last_error

        module.download_file = retry_download

    for module_name in ["minecraft_launcher_lib._helper",
                        "minecraft_launcher_lib.install",
                        "minecraft_launcher_lib.forge",
                        "minecraft_launcher_lib.mod_loader"]:
        try:
            module = __import__(module_name, fromlist=["download_file"])
            if hasattr(module, "download_file"):
                _wrap(module)
        except Exception:
            pass


def activar_red_robusta():
    _aplicar_timeout_global()
    _aplicar_reintentos_descarga()