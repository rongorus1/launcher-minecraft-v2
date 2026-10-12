#!/usr/bin/env python3
"""Test script para verificar la integración de CurseForge API."""
import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_imports():
    """Prueba que todos los módulos se importan correctamente."""
    print("Probando imports...")
    
    try:
        from helpers.curseforge_api import CurseForgeAPI
        print("[OK] CurseForgeAPI importado correctamente")
    except Exception as e:
        print(f"[FAIL] Error importando CurseForgeAPI: {e}")
        return False
    
    try:
        from helpers.manifest_parser import ManifestParser, ModDependency
        print("[OK] ManifestParser importado correctamente")
    except Exception as e:
        print(f"[FAIL] Error importando ManifestParser: {e}")
        return False
    
    try:
        from helpers.curseforge_downloader import CurseForgeDownloader
        print("[OK] CurseForgeDownloader importado correctamente")
    except Exception as e:
        print(f"[FAIL] Error importando CurseForgeDownloader: {e}")
        return False
    
    # No importar config_curseforge aquí - se importa lazy en __init__.py
    # Se prueba en test_config()
    print("[OK] ConfigCurseForge (lazy import)")
    
    try:
        from helpers import (
            CurseForgeAPI, ManifestParser, ModDependency,
            CurseForgeDownloader
        )
        print("[OK] Imports desde helpers.__init__ funcionan")
    except Exception as e:
        print(f"[FAIL] Error en imports de helpers.__init__: {e}")
        return False
    
    return True


def test_manifest_parser():
    """Prueba el parser de manifest.json"""
    print("\nProbando ManifestParser...")
    
    from helpers.manifest_parser import ManifestParser
    
    # Crear un manifest de prueba
    test_manifest = {
        "name": "Test Pack",
        "versionId": "1.0.0",
        "minecraft": {
            "version": "1.20.1",
            "modLoaders": [{"id": "forge-47.4.10", "primary": True}]
        },
        "files": [
            {
                "projectID": 531761,
                "fileID": 8545415,
                "required": True
            },
            {
                "projectID": 1095252,
                "fileID": 6261985,
                "required": True
            }
        ]
    }
    
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"name": "Test", "versionId": "1.0", "minecraft": {"version": "1.20.1"}, "files": []}, f)
        temp_path = f.name
    
    try:
        # Test validación
        from helpers.manifest_parser import ManifestParser
        valid, msg = ManifestParser.validate_manifest("nonexistent.json")
        assert not valid, "Debería fallar con archivo inexistente"
        
        # Test con archivo real
        with open("test_manifest.json", "w") as f:
            json.dump({
                "name": "Test Pack",
                "versionId": "1.0.0",
                "minecraft": {"version": "1.20.1", "modLoaders": [{"id": "forge-47.4.10", "primary": True}]},
                "files": [
                    {"projectID": 531761, "fileID": 8545415, "required": True},
                    {"projectID": 1095252, "fileID": 6261985, "required": True}
                ]
            }, f)
        
        valid, msg = ManifestParser.validate_manifest("test_manifest.json")
        assert valid, f"Validación falló: {msg}"
        print("[OK] Validación de manifest OK")
        
        manifest = ManifestParser.parse("test_manifest.json")
        assert manifest["name"] == "Test Pack"
        assert len(manifest["dependencies"]) == 2
        assert manifest["dependencies"][0]["project_id"] == 531761
        print("[OK] Parseo de manifest OK")
        
        os.remove("test_manifest.json")
        print("[OK] ManifestParser funciona correctamente")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error en test ManifestParser: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Prueba configuración de API key."""
    print("\nProbando configuración...")
    
    # Test set/get con variable de entorno - IMPORTAR DESPUÉS de setear env var
    import os
    os.environ["CURSEFORGE_API_KEY"] = "test-key-123"
    
    # Recargar módulo para que lea la nueva variable de entorno
    import importlib
    import sys
    for mod in list(sys.modules.keys()):
        if 'config_curseforge' in mod:
            del sys.modules[mod]
    importlib.invalidate_caches()
    importlib.reload(importlib.import_module('helpers.config_curseforge'))
    from helpers.config_curseforge import get_api_key, validate_api_key
    
    assert validate_api_key() == True
    assert get_api_key() == "test-key"
    print("[OK] Configuracion con variable de entorno OK")
    
    # Limpiar
    del os.environ["CURSEFORGE_API_KEY"]
    import importlib
    import sys
    for mod in list(sys.modules.keys()):
        if 'config_curseforge' in mod:
            del sys.modules[mod]
    importlib.reload(importlib.import_module('helpers.config_curseforge'))
    
    # Sin API key configurada
    from helpers.config_curseforge import validate_api_key as _validate_api_key, get_api_key as _get_api_key
    assert not _validate_api_key(), "Debería ser False sin API key"
    assert _get_api_key() == ""
    print("[OK] Validacion sin API key OK")


def test_manifest_parser():
    """Prueba el parser de manifest.json"""
    print("\nProbando ManifestParser...")
    
    from helpers.manifest_parser import ManifestParser
    
    # Crear un manifest de prueba
    test_manifest = {
        "name": "Test Pack",
        "versionId": "1.0.0",
        "minecraft": {
            "version": "1.20.1",
            "modLoaders": [{"id": "forge-47.4.10", "primary": True}]
        },
        "files": [
            {
                "projectID": 531761,
                "fileID": 8545415,
                "required": True
            },
            {
                "projectID": 1095252,
                "fileID": 6261985,
                "required": True
            }
        ]
    }
    
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"name": "Test", "versionId": "1.0", "minecraft": {"version": "1.20.1"}, "files": []}, f)
        temp_path = f.name
    
    try:
        # Test validación
        from helpers.manifest_parser import ManifestParser
        valid, msg = ManifestParser.validate_manifest("nonexistent.json")
        assert not valid, "Debería fallar con archivo inexistente"
        
        # Test con archivo real
        with open("test_manifest.json", "w") as f:
            json.dump({
                "name": "Test Pack",
                "versionId": "1.0.0",
                "minecraft": {"version": "1.20.1", "modLoaders": [{"id": "forge-47.4.10", "primary": True}]},
                "files": [
                    {"projectID": 531761, "fileID": 8545415, "required": True},
                    {"projectID": 1095252, "fileID": 6261985, "required": True}
                ]
            }, f)
        
        valid, msg = ManifestParser.validate_manifest("test_manifest.json")
        assert valid, f"Validación falló: {msg}"
        print("[OK] Validación de manifest OK")
        
        manifest = ManifestParser.parse("test_manifest.json")
        assert manifest["name"] == "Test Pack"
        assert len(manifest["dependencies"]) == 2
        assert manifest["dependencies"][0]["project_id"] == 531761
        print("[OK] Parseo de manifest OK")
        
        os.remove("test_manifest.json")
        print("[OK] ManifestParser funciona correctamente")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error en test ManifestParser: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("TEST SUITE - CurseForge Integration")
    print("=" * 60)
    
    all_ok = True
    
    all_ok &= test_imports()
    all_ok &= test_manifest_parser()
    all_ok &= test_config()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("[OK] TODOS LOS TESTS PASARON")
        return 0
    else:
        print("[FAIL] ALGUNOS TESTS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(main())