# 09 · UX de progreso, log de fases y Java en paralelo

Implementa los puntos [3], [5] y [6] de IDEAS.txt.

## [3] UX de progreso
- Nueva etiqueta de estado bajo la barra (`ProgressBarGeneric.status_label`): muestra la fase actual, el contador y la velocidad.
- `minecraft_set_status` traduce los estados de minecraft-launcher-lib a español ("Download Libraries" → "Descargando librerías", etc.) y los muestra en la etiqueta junto a "X/Y" (de `setMax`/`setProgress`) y "X MB/s" (medida por archivo descargado en `robust_network`).
- Extracción de mods (`archive_tools.extract_modpack` + `update_mods_controller`): muestra qué archivo/carpeta se está extrayendo ("Extrayendo mods/xxx.jar (12/340)") y avisa al reemplazar la carpeta `mods/`.
- Copia del juego preinstalado (`preinstalled.extraer_juego_preinstalado`): muestra "Copiando juego preinstalado: <ruta>".
- Descarga de Java (`descargar_java_17`): ahora informa "Descargando Java 17 (X/Y MB)" y "Descomprimiendo Java 17...", con progreso por bytes.

## [6] Log de fases
- Todas las fases quedan marcadas en `launcher.log` con `[Fase]`: búsqueda de Java, copia preinstalada, Minecraft (vanilla/librerías/assets/jar), Forge, lanzamiento.
- Cada descarga de archivo se registra con nombre y tamaño ("Descargado X: 4,2 MB (3,1 MB/s)") en `robust_network`; los fallos ya se logueaban por intento.
- El estado traducido de cada fase también se escribe en el log ("[Fase] Descargando librerías").

## [5] Java en paralelo
- Antes: `detectar_java()` descargaba Java secuencialmente ANTES de instalar Minecraft.
- Ahora: se comprueba rápido `java_ya_instalada()` (PATH o Java del launcher). Si no hay Java, se descarga en un hilo en paralelo con `install_minecraft_version` (librerías/assets/jar), en modo silencioso (sin messageboxes; el progreso se ve en la barra). Tras la fase Minecraft se espera al hilo de Java (los procesadores de Forge necesitan `java`) y se pasa `java=...` a `install_forge_version`.
- `descargar_java_17` acepta `progress_callback`, `status_callback` y `silencioso`, y reintenta la descarga 3 veces.

## Verificación
- `py_compile` OK de todos los módulos tocados.
- `build.bat` regenerado: exe + `juego_preinstalado.zip` (4154 archivos, 849.2 MB) + `launcher_update_1.0.0.zip` (35.0 MB).
- `RongonLang Launcher.zip` refrescado (884.2 MB) y asset de la Release v1.0.0 re-subido.
