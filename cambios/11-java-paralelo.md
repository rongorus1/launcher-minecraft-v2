# 11 · Java en paralelo

Punto [5] de IDEAS.txt.

## Problema
Si faltaba Java, `detectar_java()` lo descargaba de forma secuencial ANTES de instalar Minecraft: se perdía tiempo valioso que las librerías/descargas podían estar usando.

## Cambios
- `java_tools.py`:
  - `java_ya_instalada()`: comprueba rápido Java 17+ en el PATH o en la carpeta del launcher, sin descargar nada.
  - `ruta_java_launcher()` (pública).
  - `descargar_java_17(progress_callback, status_callback, silencioso)`: informa avance por bytes ("Descargando Java 17 (X/Y MB)"), estado de descompresión, reintenta la descarga 3 veces y con `silencioso=True` no muestra messageboxes (el progreso se ve en la barra del launcher).
- `minecraft_controller.py`:
  - Si no hay Java, se descarga en un hilo (`_descargar_java_hilo`) EN PARALELO con `install_minecraft_version` (librerías/assets/jar).
  - Tras la fase Minecraft se espera al hilo de Java (los procesadores de Forge necesitan `java`) y se pasa `java=java_path` a `install_forge_version`.
  - `options["java"]` se rellena al final con la ruta definitiva.

## Verificación
- `py_compile` OK.
- `build.bat` regenerado (exe + paquetes).