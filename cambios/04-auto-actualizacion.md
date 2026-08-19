# 04 · Auto-actualización vía GitHub Releases

## Qué cambió
- Nuevo `src/version.py`: `VERSION` (versión actual del launcher) y `GITHUB_REPO` (repo de Releases).
- Nuevo `src/helpers/updater.py`:
  - `_es_version_superior`: compara versiones semver.
  - `version_remota(repo)`: consulta la última Release de GitHub y busca el asset `launcher_update_*.zip`.
  - `descargar_actualizacion`: descarga con verificación **sha256** cuando la Release lo incluye.
  - `_extraer_seguro`: extrae con protección zip-slip.
  - `aplicar_actualizacion`: prepara `_update`, renombra `RongonLang Launcher.exe` y `_internal` a `.new`, escribe `actualizar.bat` que espera la salida del exe, intercambia, relanza y se autoborra.
  - `lanzar_actualizacion`: ejecuta el bat.
- `src/views/main_window.py`: comprobación automática al arrancar (**solo** en el exe compilado, no en `python src/main.py`) y diálogo "Hay una nueva versión".
- Nuevo `empaquetar_actualizacion.py`: genera `launcher_update_<version>.zip` (solo código: exe + `_internal`, SIN el juego) y `version.json`.
- `build.bat`: añadido el paso [5/5].

## Verificación
- Pruebas unitarias: comparación de versiones y preparación del intercambio (el zip del juego no se toca).
- El check remoto no rompe si no hay Release (404 → no hay actualización).