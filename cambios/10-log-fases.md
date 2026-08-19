# 10 · Log de fases

Punto [6] de IDEAS.txt.

## Cambios
- `robust_network.py`: cada descarga completada se registra en `launcher.log` con nombre y tamaño ("Descargado x.jar: 4,2 MB"). Los fallos ya se registraban por intento.
- `minecraft_controller.py`: todas las fases quedan marcadas en el log con prefijo `[Fase]`:
  - `minecraft_set_status`: el estado de la librería (Java / librerías / assets / Forge / instalación) se escribe como `[Fase] ...`.
  - `_instalar_con_reintentos`: "intento X/3", "completada", "error" y "se reintentara" con `[Fase]`.
  - `ejecutar_minecraft`: "Copiando juego preinstalado", "Minecraft: verificando/descargando librerias, assets y jar", "Forge: instalando procesadores y verificando" y "Lanzando Minecraft".

Con esto se puede diagnosticar en qué fase y con qué archivo/tamaño se quedó una instalación (como el bug del 66%).

## Verificación
- `py_compile` OK.
- `build.bat` regenerado (exe + paquetes).