# Contribuyendo a RongonLang Launcher

Gracias por querer contribuir. Estas guías mantienen el proyecto organizado y consistente.

## Antes de empezar

- Para dudas de uso o soporte, usa [Discord](https://discord.gg/kZWQrwb64p).
- Para reportar un bug o pedir una función, abre un **issue** con su plantilla.
- Para reportar una vulnerabilidad, sigue [SECURITY.md](SECURITY.md) (no la expongas en un issue).

## Flujo de trabajo

El proyecto usa un flujo basado en ramas y Pull Requests:

1. Crea una rama desde `main` con el nombre `cambio/<n>-<descripcion>` (n = número del cambio).
2. Haz tus cambios con commits pequeños y mensajes claros.
3. Añade una entrada al `CHANGELOG.md` y un documento `cambios/<n>-<descripcion>.md` explicando qué cambió y por qué.
4. Abre un Pull Request contra `main` (se revisará automáticamente y debe pasar la CI).
5. `main` está protegido: requiere revisión y los checks en verde.

## Estándares de código

- Python 3.10+, sin dependencias nuevas sin justificarlo en el PR.
- Sigue el estilo existente del proyecto (sin comentarios innecesarios, nombres descriptivos).
- Verifica que compila antes de abrir el PR:

  ```sh
  python -m compileall -q src/
  ```

## Actualizar el launcher en GitHub

La versión se define en `src/version.py`. Para publicar una Release, sigue la sección "Publicar una actualización" del [README](README.md).

## Código de conducta

Participar en este proyecto implica aceptar el [Código de Conducta](CODE_OF_CONDUCT.md).