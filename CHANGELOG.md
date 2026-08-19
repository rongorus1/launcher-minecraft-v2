# Changelog

Cada cambio tiene su propia rama (`cambio/<n>-<nombre>`) con un registro detallado en `cambios/`.

## v1.0.0 — 2026-08-18

### 01 · Modpacks RAR/ZIP sin programas externos
`cambio/01-modpacks-rar-zip-sin-externos`
Extracción de modpacks RAR/ZIP sin instalar nada (usa `unrar2-cffi`, librería incluida). Se elimina la dependencia de `rarfile` + binario externo. El extractor quita la carpeta envolvente y coloca `mods/`, `config/`, `kubejs/`, `scripts/` directamente en `.minecraft`.

### 02 · Descarga robusta y reparación automática
`cambio/02-descarga-robusta`
Arregla la instalación que se quedaba colgada toda la noche al 66% (socket congelado, `requests` sin timeout). Nuevo `helpers/robust_network.py`: timeouts globales (15s/120s) y reintentos por archivo. El controlador reintenta (x3), reanuda y **siempre** repara la instalación antes de jugar.

### 03 · Juego preinstalado
`cambio/03-juego-preinstalado`
`empaquetar_juego.py` genera `juego_preinstalado.zip` (817 MB) dentro de la carpeta del launcher. En el primer arranque el juego se copia desde el zip (1-2 min) en vez de descargar GB. Si no hay zip, se descarga normal y las copias a medias se auto-reparan.

### 04 · Auto-actualización vía GitHub Releases
`cambio/04-auto-actualizacion`
`version.py` + `helpers/updater.py`: al arrancar comprueba la última Release del repo, descarga `launcher_update_*.zip` con verificación sha256, aplica el intercambio en caliente (`actualizar.bat`) y relanza. `empaquetar_actualizacion.py` genera el paquete de actualización (solo código).

### 05 · Empaquetado en dist/distribucion
`cambio/05-empaquetado-distribucion`
`build.bat` de 5 pasos compila directamente en `dist/distribucion` (el único lugar con el ejecutable) y añade `Rongoland.rar` e `INSTRUCCIONES.txt`.

### 06 · Paquete único de reparto
`cambio/06-paquete-reparto`
`comprimir_paquete.py` genera `RongonLang Launcher.zip` (~850 MB) para compartir: un solo archivo que el jugador descomprime y ejecuta. El modpack (`Rongoland.rar`) se entrega aparte a propósito.