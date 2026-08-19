# 03 · Juego preinstalado

## Qué cambió
- Nuevo `empaquetar_juego.py`: crea `juego_preinstalado.zip` (817 MB, 4129 archivos) con `versions/`, `libraries/`, `assets/` y `runtime/` desde el `.minecraft` local.
- Nuevo `src/helpers/preinstalled.py`:
  - `buscar_juego_preinstalado()`: busca el zip en la carpeta del exe, la de su padre, el directorio de trabajo y la raíz del proyecto.
  - `extraer_juego_preinstalado(zip, minecraft_dir, progress_callback)`: protección **zip-slip**, salta archivos del mismo tamaño (reanudable), progreso en bytes.
- `src/controller/minecraft_controller.py`: si hace falta instalar desde cero y existe el zip → **copia desde el zip (1-2 min)** en vez de descargar GB. Si no hay zip → descarga normal; una copia parcial se repara sola al siguiente arranque.

## Resultado
- El jugador ya no descarga ~1 GB: solo descomprime el paquete y el primer arranque copia el juego.
- Verificado: CRC del zip OK, extracción real a una carpeta limpia OK (forge_json y runtime Java quedan en su sitio), smoke test OK.