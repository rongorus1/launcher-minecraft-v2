# RongonLang Launcher (v2)

Lanzador personalizado para Minecraft **1.20.1 + Forge 47.3.0** con conexión automática al servidor `X.MINEMU.NET:11127`, instalación de modpacks RAR/ZIP sin programas externos, juego preinstalado y auto-actualización desde GitHub Releases.

## Novedades de la v2

- **Juego preinstalado**: `build.bat` empaqueta el juego dentro de `juego_preinstalado.zip` junto al ejecutable. El jugador solo descomprime y copia (1-2 min) en vez de descargar GB.
- **Descarga robusta**: timeouts globales (15s/120s) y reintentos por archivo (`helpers/robust_network.py`). Una instalación nunca se cuelga en silencio; se reanuda y se repara automáticamente.
- **Auto-actualización**: al iniciar comprueba la última Release de GitHub; si hay una versión nueva descarga `launcher_update_<version>.zip`, lo aplica en caliente y reinicia.
- **Modpacks RAR/ZIP** sin instalar nada (usa `unrar2-cffi`, librería incluida). Quita la carpeta envolvente, coloca `mods/`, `config/`, `kubejs/`, `scripts/`, etc. directamente en `.minecraft` y solo reemplaza `mods/` si el modpack trae mods.

## Requisitos
- Python 3.10 o superior (para ejecutar desde código)
- Java 17 (el lanzador puede descargarlo automáticamente)
- Dependencias: `pip install -r src/requirements.txt`

## Uso
```sh
python src/main.py
```

- Inicia sesión y crea perfiles.
- Configura la RAM (4-16 GB) en "Configuración RAM".
- "Play" conecta automáticamente a `X.MINEMU.NET:11127` con Forge.

## Configuración
Edita `src/config/__init__.py` (versiones de Minecraft/Forge, servidor, nombre del launcher) y `src/version.py` (versión actual del launcher y repositorio de Releases).

## Empaquetar (crear el paquete para repartir)
```bat
build.bat
```
Compila directamente en `dist/distribucion/` (el ÚNICO lugar con el ejecutable) y genera:
- `RongonLang Launcher\` → ejecutable + `_internal\` + `juego_preinstalado.zip` (817 MB)
- `Rongoland.rar` + `INSTRUCCIONES.txt`
- `launcher_update_<version>.zip` + `version.json` → para subir a la Release de GitHub

Para el archivo único de reparto: `python comprimir_paquete.py` (crea `RongonLang Launcher.zip`, ~850 MB, con el zip del juego sin comprimir dentro para extracción rápida).

Scripts de empaquetado:
- `empaquetar_juego.py` → genera `juego_preinstalado.zip` (versiones, librerías, assets, runtime Java).
- `empaquetar_actualizacion.py` → genera `launcher_update_<version>.zip` (solo código: exe + `_internal`, sin el juego).

## Publicar una actualización
1. Bump de versión en `src/version.py`.
2. `build.bat` (genera el nuevo `launcher_update_*.zip`).
3. Crear una Release en GitHub con tag `v<version>` y subir el `launcher_update_*.zip` como asset.

## Créditos
- [minecraft-launcher-lib](https://github.com/JakobDev/minecraft-launcher-lib)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)