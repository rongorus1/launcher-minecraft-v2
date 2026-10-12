# src/helpers/curseforge_downloader.py
"""Descargador de mods desde CurseForge usando manifest.json."""
import logging
import os
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class CurseForgeDownloader:
    """Descargador de mods desde CurseForge usando manifest.json."""
    
    def __init__(
        self, 
        api_key: str, 
        minecraft_dir: str,
        max_concurrent: int = 4
    ):
        """
        Args:
            api_key: API Key de CurseForge (obtener en console.curseforge.com)
            minecraft_dir: Directorio .minecraft del modpack
            max_concurrent: Descargas simultáneas máximas (no implementado aún, secuencial por ahora)
        """
        self.api_key = api_key
        self.minecraft_dir = Path(minecraft_dir)
        self.mods_dir = self.minecraft_dir / "mods"
        self.max_concurrent = max_concurrent
        self.mods_dir.mkdir(parents=True, exist_ok=True)
        self._stop_event = threading.Event()
        
        # Inicializar API
        if api_key:
            from helpers.curseforge_api import CurseForgeAPI
            self.api = CurseForgeAPI(api_key)
        else:
            self.api = None
    
    def stop(self):
        """Cancela las descargas en curso."""
        self._stop_event.set()
    
    def install_from_manifest(
        self,
        manifest_path: str,
        api_key: str = None,
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Instala todas las dependencias del manifest.json.
        
        Args:
            manifest_path: Ruta al manifest.json
            api_key: API Key de CurseForge (opcional, usa el del constructor si no se pasa)
            progress_callback: callback(actual, total)
            status_callback: callback(texto_estado)
            
        Returns:
            dict: {"success": bool, "installed": int, "failed": list, "skipped": int, "total": int}
        """
        from helpers.manifest_parser import ManifestParser
        from helpers.config_curseforge import get_api_key
        from helpers.curseforge_api import CurseForgeAPI
        
        # Usar api_key pasado o del constructor o de config
        if not api_key:
            api_key = self.api_key or get_api_key()
        
        if not api_key:
            return {"success": False, "error": "Se requiere API Key de CurseForge (CURSEFORGE_API_KEY)", "installed": 0, "failed": [], "skipped": 0, "total": 0}
        
        # Validar manifest
        valid, msg = ManifestParser.validate_manifest(manifest_path)
        if not valid:
            return {"success": False, "error": f"Manifest inválido: {msg}", "installed": 0, "failed": [], "skipped": 0, "total": 0}
        
        manifest = ManifestParser.parse(manifest_path)
        dependencies = manifest.get("dependencies", [])
        
        if not dependencies:
            logger.warning("No hay dependencias requeridas en el manifest")
            return {"success": True, "installed": 0, "skipped": 0, "failed": [], "total": 0}
        
        # Inicializar API si no existe o con nueva key
        if not self.api or self.api.api_key != api_key:
            self.api = CurseForgeAPI(api_key)
        
        results = {
            "success": True,
            "installed": 0,
            "skipped": 0,
            "failed": [],
            "total": len(dependencies)
        }
        
        # Crear directorio de mods
        self.mods_dir.mkdir(parents=True, exist_ok=True)
        
        # Descargar cada dependencia secuencialmente
        for i, dep in enumerate(dependencies):
            if self._stop_event.is_set():
                logger.info("Descarga cancelada por usuario")
                break
            
            project_id = dep["project_id"]
            file_id = dep["file_id"]
            
            # Callback de estado
            if status_callback:
                status_callback(f"Descargando {project_id}/{file_id} ({i+1}/{len(dependencies)})")
            
            # Verificar si ya existe (por nombre con project_file id)
            dest_path = self.mods_dir / f"{project_id}_{file_id}.jar"
            # También verificar si ya existe por nombre original (si se descargó antes con otro nombre)
            if dest_path.exists():
                logger.info(f"Mod ya existe, saltando: {project_id}_{file_id}")
                results["skipped"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(dependencies))
                continue
            
            # Descargar
            success = self._download_mod(
                project_id=project_id,
                file_id=file_id,
                dest_path=dest_path,
            )
            
            if not success:
                results["failed"].append({
                    "project_id": project_id,
                    "file_id": file_id,
                    "error": "Falló descarga tras reintentos"
                })
            else:
                results["installed"] += 1
            
            if progress_callback:
                progress_callback(i + 1, len(dependencies))
        
        results["success"] = len(results["failed"]) == 0
        return results
    
    def _download_mod(
        self, 
        project_id: int, 
        file_id: int, 
        dest_path: Path,
    ) -> bool:
        """Descarga un mod individual con reintentos."""
        dest_path = Path(dest_path)
        
        # Verificar si ya existe
        if dest_path.exists():
            logger.info(f"Archivo ya existe, saltando: {dest_path.name}")
            return True
        
        for attempt in range(3):
            try:
                # Obtener URL de descarga
                download_url = self.api.get_file_download_url(project_id, file_id)
                if not download_url:
                    logger.error(f"No se pudo obtener URL de descarga para {project_id}/{file_id}")
                    return False
                
                # Descargar con streaming
                resp = requests.get(
                    download_url,
                    stream=True,
                    timeout=(15, 300),
                    headers={"User-Agent": "RongonLang-Launcher/1.0"}
                )
                resp.raise_for_status()
                
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(dest_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"Descargado: {dest_path.name}")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt + 1} fallido: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Falló descarga tras 3 intentos: {e}")
                    # Limpiar archivo parcial
                    if dest_path.exists():
                        try:
                            dest_path.unlink()
                        except:
                            pass
                    return False
        
        return False
