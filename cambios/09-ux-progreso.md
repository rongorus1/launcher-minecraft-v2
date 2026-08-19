# 09 · UX de progreso

Punto [3] de IDEAS.txt.

## Cambios
- `ProgressBarGeneric` (components/progress_bar_generic.py): nueva etiqueta de estado (`status_label`) bajo la barra, con `set_status` y `set_status_thread_safe`. Se muestra/oculta junto con la barra.
- `MinecraftController` (controller/minecraft_controller.py):
  - Traducción de los estados de minecraft-launcher-lib a español (`_traducir_estado`: "Download Libraries" → "Descargando librerías", etc.).
  - `minecraft_set_status`/`_actualizar_estado_ui`: muestra en la etiqueta la fase, el contador "X/Y" (de `setMax`/`setProgress`) y "X MB/s".
  - `minecraft_set_max` conserva `progress_bar_value_total` (sin esto la barra se quedaba en 0%).
  - `_estado_preinstalado`: muestra cada archivo de la copia del juego preinstalado.
- Extracción de mods (`archive_tools.extract_modpack` + `update_mods_controller`): nuevo `status_callback` que muestra el archivo/carpeta que se está extrayendo ("Extrayendo mods/xxx.jar (12/340)") y avisa al reemplazar la carpeta `mods/`.
- Copia preinstalada (`preinstalled.extraer_juego_preinstalado`): nuevo `status_callback` con la ruta que se copia.
- `robust_network.py`: mide la velocidad (MB/s) de la última descarga completada (`obtener_velocidad_ultima_mbps`) para mostrarla en la barra.

## Verificación
- `py_compile` OK.
- `build.bat` regenerado (exe + paquetes) y probado en la compilación.