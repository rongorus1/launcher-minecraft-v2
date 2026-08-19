# 05 · Empaquetado en dist/distribucion

## Qué cambió
- Nuevo `build.bat` con pipeline de **5 pasos**:
  - [1/5] Instalar dependencias.
  - [2/5] Compilar con PyInstaller **directamente** en `dist/distribucion` (el ÚNICO lugar con el ejecutable). Modo `onedir` para un arranque rápido.
  - [3/5] Generar `juego_preinstalado.zip` dentro de la carpeta del launcher.
  - [4/5] Copiar `Rongoland.rar` (modpack) e `INSTRUCCIONES.txt`.
  - [5/5] Generar `launcher_update_<version>.zip` + `version.json`.
- Nuevo `INSTRUCCIONES.txt`: guía de instalación y uso para el jugador.

## Resultado
- El paquete final vive en `dist/distribucion\` y contiene la carpeta `RongonLang Launcher\` (exe + `_internal\` + `juego_preinstalado.zip`), `Rongoland.rar` e `INSTRUCCIONES.txt`.
- Se acabaron las carpetas de compilación dispersas: una sola ubicación autoritativa.