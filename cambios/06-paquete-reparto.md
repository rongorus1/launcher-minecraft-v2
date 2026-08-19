# 06 · Paquete único de reparto

## Qué cambió
- Nuevo `comprimir_paquete.py`: crea **`RongonLang Launcher.zip`** (~850 MB, 1024 archivos, CRC verificado) con el ejecutable + `_internal` + `juego_preinstalado.zip` **guardado sin comprimir** para una extracción rápida.
- El `juego_preinstalado.zip` vive dentro de la carpeta del launcher para que baste con compartir una sola carpeta.

## Flujo para el jugador
1. Recibe UN solo archivo: `RongonLang Launcher.zip`.
2. Descomprime y ejecuta el launcher.
3. En el primer arranque copia el juego desde el zip interno (1-2 min) y ya puede jugar.
4. `Rongoland.rar` (el modpack) se entrega **aparte a propósito**: si cambia el modpack, el jugador recibe un rar nuevo.