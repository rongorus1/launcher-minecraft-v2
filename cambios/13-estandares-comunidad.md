# 13 · Estándares de comunidad

## Qué se hizo

- **`LICENSE`**: licencia MIT (el repo era público sin licencia = "todos los derechos reservados").
- **`README.md`**: reescrito con insignias (versión/licencia/Python/tamaño), logo, sección para jugadores (instalación rápida) y para desarrolladores (estructura, build, publicación), datos corregidos (Forge 47.4.0, ~849 MB juego, ~1.36 GB paquete de reparto).
- **`.github/ISSUE_TEMPLATE/`**: plantillas de bug y de feature (formularios YAML) + `config.yml` que enlaza Discord y el Security Advisory.
- **`.github/pull_request_template.md`**: checklist de verificación para cada PR.
- **`CONTRIBUTING.md`**: guía del flujo de trabajo (ramas, CHANGELOG, CI).
- **`CODE_OF_CONDUCT.md`**: Contributor Covenant 2.1 en español.
- **`SECURITY.md`**: cómo reportar vulnerabilidades de forma privada y versiones soportadas.
- **`.github/workflows/ci.yml`**: compila todos los módulos en cada push a `main` y en cada PR.
- **`.gitattributes`**: normalización de saltos de línea.

## Por qué

Un repo público con buenas prácticas de comunidad se ve más profesional, es
descubrible (topics), invita a contribuir (plantillas y guías) y protege al
autor (licencia, canal privado de seguridad). La CI verifica que ningún PR rompa
la compilación.

## Cómo se aplicó

La parte de GitHub (topics, `delete_branch_on_merge`, Discussions, labels y
status check obligatorio en `main`) se configuró por API tras fusionar este PR;
el resto son archivos del repo.