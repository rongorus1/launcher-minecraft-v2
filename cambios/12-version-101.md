# 12 · Versión 1.0.1

## Rama
`cambio/12-version-101`

## Qué cambia
`src/version.py`: `VERSION` pasa de `"1.0.0"` a `"1.0.1"`.

## Por qué
1. **Auto-actualización**: con la versión igual a la Release (1.0.0), `helpers/updater.py` no detectaba versión superior y los launchers ya instalados nunca se actualizaban. Con 1.0.1 la comprobación `_es_version_superior("1.0.1", "1.0.0")` es cierta y el launcher descarga el nuevo `launcher_update_1.0.1.zip`.
2. **Corrección incluida**: este exe (y el paquete completo) se reconstruyen desde `main`, que ya tiene `FORGE_VERSION = "47.4.0"`. El paquete anterior llevaba un exe compilado desde una rama basada en el main viejo, con `47.3.0` embebido, y por eso el juego arrancaba con la versión anterior de Forge.

## Cómo se publica
1. Rebuild del exe desde `main` (`build.bat` con el python de Python314).
2. `empaquetar_actualizacion.py` genera `launcher_update_1.0.1.zip` + `version.json`.
3. `comprimir_paquete.py` regenera `RongonLang Launcher.zip` (mantiene `Rongoland.rar`).
4. Release nueva `v1.0.1` en GitHub con `launcher_update_1.0.1.zip` como asset.

## Archivos tocados
- `src/version.py`
- `CHANGELOG.md`
- `cambios/12-version-101.md`