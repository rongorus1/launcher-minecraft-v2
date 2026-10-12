# src/helpers/manifest_parser.py
"""Parser para manifest.json de modpacks CurseForge/Modrinth."""
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class ModDependency:
    """Representa una dependencia de mod en el manifest."""
    project_id: int
    file_id: int
    required: bool = True
    name: str = ""
    file_name: str = ""


class ManifestParser:
    """Parser para manifest.json de modpacks CurseForge/Modrinth."""
    
    @staticmethod
    def parse(manifest_path: str) -> dict:
        """
        Parsea un manifest.json y retorna estructura normalizada.
        
        Returns:
            dict con keys: name, version, minecraft_version, forge_version, dependencies
        """
        path = Path(manifest_path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest no encontrado: {manifest_path}")
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraer info básica
        minecraft_info = data.get("minecraft", {})
        mod_loaders = minecraft_info.get("modLoaders", [])
        forge_version = ""
        for loader in mod_loaders:
            if "forge" in loader.get("id", "").lower():
                forge_version = loader.get("id", "").replace("forge-", "")
                break
        
        # Parsear dependencias
        dependencies = []
        for dep in data.get("files", []):
            if not dep.get("required", True):
                continue  # Solo dependencias requeridas
            
            dep_info = {
                "project_id": dep.get("projectID"),
                "file_id": dep.get("fileID"),
                "required": dep.get("required", True),
                "name": "",
                "file_name": f"{dep.get('projectID')}_{dep.get('fileID')}.jar"
            }
            
            # Validar campos requeridos
            if dep.get("projectID") and dep.get("fileID"):
                dependencies.append(dep)
        
        return {
            "name": data.get("name", "Unknown Modpack"),
            "version": data.get("version", data.get("versionId", "1.0.0")),
            "minecraft_version": minecraft_info.get("version", "1.20.1"),
            "forge_version": forge_version.replace("forge-", "") if forge_version else "47.4.10",
            "dependencies": [
                {
                    "project_id": d.get("projectID"),
                    "file_id": d.get("fileID"),
                    "required": d.get("required", True),
                    "name": "",
                    "file_name": f"{d.get('projectID')}_{d.get('fileID')}.jar"
                }
                for d in data.get("files", [])
                if d.get("projectID") and d.get("fileID") and d.get("required", True)
            ]
        }
    
    @staticmethod
    def validate_manifest(manifest_path: str) -> tuple[bool, str]:
        """
        Valida que el manifest tenga la estructura mínima requerida.
        
        Returns:
            (bool, mensaje_error)
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {e}"
        except Exception as e:
            return False, f"Error leyendo archivo: {e}"
        
        # Validar campos obligatorios (versionId es opcional: el export
        # CurseForge usa "version")
        required_fields = ["name", "minecraft", "files"]
        for field in required_fields:
            if field not in data:
                return False, f"Campo requerido faltante: {field}"
        if "version" not in data and "versionId" not in data:
            return False, "Falta 'version' (o 'versionId') del modpack"
        
        if "version" not in data.get("minecraft", {}):
            return False, "minecraft.version requerido"
        
        if not isinstance(data.get("files"), list) or not data["files"]:
            return False, "Se requiere al menos un archivo en 'files'"
        
        # Validar cada archivo
        for i, file_entry in enumerate(data.get("files", [])):
            if not isinstance(file_entry, dict):
                return False, f"Entrada {i} en 'files' debe ser un objeto"
            
            required_fields = ["projectID", "fileID", "required"]
            for field in ["projectID", "fileID"]:
                if field not in file_entry:
                    return False, f"Entrada {i}: campo '{field}' requerido"
            
            if not isinstance(file_entry.get("projectID"), int):
                return False, f"Entrada {i}: projectID debe ser entero"
            if not isinstance(file_entry.get("fileID"), int):
                return False, f"Entrada {i}: fileID debe ser entero"
        
        return True, "OK"