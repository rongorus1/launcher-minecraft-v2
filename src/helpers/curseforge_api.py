# src/helpers/curseforge_api.py
"""Cliente para la API de CurseForge."""
import logging
import os
import time
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)

# Configuración de timeouts
_CONNECT_TIMEOUT = 15
_READ_TIMEOUT = 120
_MAX_RETRIES = 3
_RETRY_BACKOFF = 2  # segundos base para backoff exponencial


class CurseForgeAPI:
    """Cliente para la API de CurseForge (v1)."""
    
    BASE_URL = "https://api.curseforge.com/v1"
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Se requiere API key de CurseForge")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Accept": "application/json",
            "User-Agent": "RongonLang-Launcher/1.0"
        })
        self._configure_retries()
    
    def _configure_retries(self):
        """Configura adaptador con reintentos automáticos."""
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Realiza petición con manejo de errores y rate limiting."""
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = self.session.request(
                    method,
                    url,
                    timeout=(15, 60),
                    **kwargs
                )

                # Rate limiting
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited. Esperando {retry_after}s...")
                    time.sleep(retry_after)
                    continue

                resp.raise_for_status()
                return resp

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {attempt}/{_MAX_RETRIES}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error de red (intento {attempt}/{_MAX_RETRIES}): {e}")

            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF ** attempt)  # Backoff exponencial

        logger.error(f"Falló después de {_MAX_RETRIES} intentos: {url}")
        return None

    def validate_key(self) -> bool:
        """Verifica la key contra la API (GET /v1/games). False = inválida/revocada."""
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/games",
                timeout=(10, 20),
            )
            return resp.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"No se pudo validar la API key: {e}")
            return False
    
    def get_file_download_url(self, project_id: int, file_id: int) -> Optional[str]:
        """Obtiene la URL de descarga directa (sigue redirect 302)."""
        url = f"{self.BASE_URL}/mods/{project_id}/files/{file_id}/download"
        
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/mods/{project_id}/files/{file_id}/download",
                allow_redirects=False,
                timeout=(15, 30),
                headers={"Accept": "application/json"}
            )
            
            if resp.status_code == 302:
                return resp.headers.get("Location")
            elif resp.status_code == 200:
                # A veces devuelve JSON directo
                data = resp.json()
                return data.get("data", {}).get("downloadUrl") or data.get("downloadUrl")
            
            logger.warning(f"Respuesta inesperada {resp.status_code} para {project_id}/{file_id}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo URL de descarga: {e}")
            return None
    
    def get_file_info(self, project_id: int, file_id: int) -> Optional[Dict]:
        """Obtiene información del archivo (metadatos, hash, nombre, etc.)."""
        url = f"{self.BASE_URL}/mods/{project_id}/files/{file_id}"
        
        try:
            resp = self._get(f"/mods/{project_id}/files/{file_id}")
            if resp and resp.status_code == 200:
                return resp.json().get("data")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo info de archivo: {e}")
            return None
    
    def _get(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """GET con reintentos y manejo de rate limiting."""
        for attempt in range(3):
            try:
                resp = self.session.get(
                    f"{self.BASE_URL}{endpoint}",
                    timeout=(15, 60)
                )
                
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited. Esperando {resp.headers.get('Retry-After', 60)}s")
                    time.sleep(retry_after)
                    continue
                
                resp.raise_for_status()
                return resp
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento fallido: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        
        return None
    
    def download_file(
        self, 
        project_id: int, 
        file_id: int, 
        dest_path: str,
        progress_callback: Optional[callable] = None,
        expected_sha1: Optional[str] = None
    ) -> bool:
        """Descarga un archivo con progreso y verificación de hash."""
        download_url = self.get_file_download_url(project_id, file_id)
        if not download_url:
            logger.error(f"No se pudo obtener URL de descarga para {project_id}/{file_id}")
            return False
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        for attempt in range(3):
            try:
                resp = requests.get(
                    download_url,
                    stream=True,
                    timeout=(15, 300),
                    headers={"User-Agent": "RongonLang-Launcher/1.0"}
                )
                resp.raise_for_status()
                
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                with open(dest_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verificar hash si se proporcionó
                if expected_sha1:
                    import hashlib
                    with open(dest_path, 'rb') as f:
                        actual_sha1 = hashlib.sha1(f.read()).hexdigest()
                    if actual_sha1.lower() != expected_sha1.lower():
                        logger.error(f"Hash mismatch para {dest_path}")
                        os.remove(dest_path)
                        return False
                
                logger.info(f"Descargado: {dest_path}")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento fallido: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Falló descarga tras 3 intentos: {e}")
                    return False
        
        return False