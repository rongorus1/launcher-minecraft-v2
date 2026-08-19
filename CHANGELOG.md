# Changelog

Cada cambio tiene su propia rama (`cambio/<n>-<nombre>`) con un registro detallado en `cambios/`.

## Correcciones posteriores a v1.0.0

### 09 · UX de progreso
`cambio/09-ux-progreso`
Punto [3] de IDEAS.txt. Barra con etiqueta de estado bajo ella (fase traducida a español, contador X/Y, archivo actual y MB/s). La extracción de mods muestra el archivo/carpeta que se está leyendo y la copia preinstalada muestra cada archivo.

### 10 · Log de fases
`cambio/10-log-fases`
Punto [6] de IDEAS.txt. Marcas `[Fase]` en `launcher.log` (Java / vanilla / librerías / Forge / assets / lanzamiento) y cada descarga registrada con nombre y tamaño, para diagnosticar dónde se quedó una instalación.

### 11 · Java en paralelo
`cambio/11-java-paralelo`
Punto [5] de IDEAS.txt. Si falta Java 17 se descarga en paralelo con las librerías de Minecraft (antes secuencial); se espera antes de Forge y se le pasa a su instalación.

### 08 · Forge 47.4.0
`cambio/08-forge-4740`
`FORGE_VERSION` pasa a 47.4.0 (un mod del modpack lo requiere). `empaquetar_juego.py` lee la versión dinámicamente de la config para el marcador del zip preinstalado. Recompilado, actualizado el asset de la Release v1.0.0 y el paquete de reparto.

### 07 · Fix extracción RAR en el ejecutable (cffi)
`cambio/07-fix-cffi-rar`
El exe compilado fallaba al abrir el RAR (`No module named '_cffi_backend'`): PyInstaller no detectaba el import perezoso `from unrar.cffi import rarfile`. Se añadieron los hidden imports `cffi`, `_cffi_backend` y `unrar.cffi.rarfile` a `build.bat`.

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