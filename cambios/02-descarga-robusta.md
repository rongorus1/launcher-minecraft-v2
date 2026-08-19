# 02 · Descarga robusta y reparación automática

## Problema que resolvió
Una instalación se quedaba **colgada al 66% durante toda la noche** sin ningún error en el log (descargando assets en 22:51:56 y nunca más). Causa raíz:
- `minecraft-launcher-lib` llama a `requests.get(...)` **sin timeout**.
- `shutil.copyfileobj` se queda bloqueado para siempre ante un socket congelado.
- `install_libraries` se traga las excepciones con `except: pass`, así que no hay reintento ni aviso.

## Qué cambió
- Nuevo `src/helpers/robust_network.py`:
  - Inyecta **timeouts globales** (15s de conexión / 120s de lectura) en `requests.sessions.Session.request`.
  - Envuelve `download_file` con **reintentos por archivo (x3)**.
  - Aplicado a los módulos `_helper`, `install`, `forge` y `mod_loader` de `minecraft-launcher-lib`.
- `src/main.py`: importa `activar_red_robusta()` al inicio.
- `src/controller/minecraft_controller.py`:
  - `_instalar_con_reintentos` (3 intentos; los archivos válidos se saltan por sha1, así que reanuda).
  - **Siempre** ejecuta `install_minecraft_version` antes de jugar → repara o reanuda instalaciones a medias.

## Verificación
- Pruebas unitarias de los reintentos y del parche de timeouts.
- La instalación completa de Minecraft + Forge se terminó con éxito (antes se colgaba).
- El juego llegó al menú principal.