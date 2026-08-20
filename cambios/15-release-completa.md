# 15 · Release completa v1.0.2

## Contexto

Las releases **v1.0.0 y v1.0.1 eran pruebas de auto-actualización**: solo llevaban el
asset `launcher_update_*.zip` (el .exe + `_internal`). Un jugador que descargara de la
Release se quedaba sin el juego preinstalado ni el modpack.

La **v1.0.2** es la primera release **completa** para jugadores.

## Qué se corrige

- `comprimir_paquete.py` ahora **excluye `Rongoland.rar` y `launcher.log`** del paquete
  de reparto. El modpack se entrega aparte, como indicaba el diseño original (CHANGELOG 06):
  `RongonLang Launcher.zip` queda en ~850 MB (launcher + juego preinstalado).
- `VERSION` pasa a **1.0.2**.

## Cómo se publica la release completa

1. `build.bat`: recompila el exe 1.0.2, regenera `juego_preinstalado.zip`, copia
   `Rongoland.rar` e `INSTRUCCIONES.txt` y genera `launcher_update_1.0.2.zip`.
2. `python comprimir_paquete.py`: genera `RongonLang Launcher.zip` (sin el modpack).
3. Release **v1.0.2** en GitHub con assets:
   - `RongonLang Launcher.zip` (~850 MB) — el launcher completo para el jugador.
   - `Rongoland.rar` (~483 MB) — el modpack, por separado.
   - `launcher_update_1.0.2.zip` (~35 MB) — para que los launchers 1.0.0/1.0.1 ya
     instalados se auto-actualicen a 1.0.2.

## Cómo juega un amigo

1. Descarga `RongonLang Launcher.zip` y `Rongoland.rar` de la Release.
2. Descomprime el zip y ejecuta `RongonLang Launcher.exe` (aviso de SmartScreen normal).
3. Primera vez: el launcher copia `juego_preinstalado.zip` (~1-2 min) y ya está listo.
4. Pulsa **Actualizar mods** y selecciona `Rongoland.rar` (se instalan los 119 mods).
5. Inicia sesión y pulsa **Play**.