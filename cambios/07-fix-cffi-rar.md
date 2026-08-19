# 07 · Fix extracción RAR en el ejecutable (cffi)

## Problema
Al probar el launcher compilado, "Actualizar mods" fallaba al abrir el RAR:
`No module named '_cffi_backend'` (launcher.log).

## Causa
- `src/helpers/archive_tools.py` importa `from unrar.cffi import rarfile` **dentro** de la función (import perezoso).
- PyInstaller no detecta los imports perezosos → dejó fuera el paquete `cffi` y su extensión `_cffi_backend` del ejecutable.

## Solución
- `build.bat`: añadidos los hidden imports `cffi`, `_cffi_backend` y `unrar.cffi.rarfile` al comando de PyInstaller.
- Verificado: `_internal\cffi\_cffi_backend.cp314-win_amd64.pyd` presente en el build.

## Verificación
- Recompilado el ejecutable y probado: la extracción de `Rongoland.rar` funciona correctamente en el exe.