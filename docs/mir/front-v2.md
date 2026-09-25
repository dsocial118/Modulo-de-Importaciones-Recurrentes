# Front v2 (React)

**Estado al 25-09-2026:** la base está armada y la primera pantalla, Inicio,
funciona de punta a punta. El resto sigue en la versión actual y se migra de a
una. Rama `front-react`.

## Por qué, y con qué reglas

SISOC decidió pasar su front a React con el diseño nuevo de UI/UX (issue
secretarianaf/SISOC#2577) y fijó las reglas en
`docs/implementaciones/frontend_v2.md` y
`docs/registro/decisiones/2026-09-24-frontend-v2-react.md` de su repositorio.
El MIR las sigue **al pie de la letra**, para que integrarlo no obligue a
rehacer el front:

- **Convive con el viejo.** El front nuevo vive en `/v2/mir/`; las pantallas
  actuales siguen donde están. Una sección que todavía no se migró lleva a la
  pantalla actual, marcada en el menú.
- **Mismo stack y mismas versiones exactas**: React 19.2.4, Vite 7.3.1,
  TypeScript 5.9.3, Material UI 9.4.0, Node 22.14.0.
- **El tema del skill `tema-verde-institucional`, sin modificar**, en un paquete
  compartido. Las pantallas usan roles del tema, nunca colores sueltos, y los
  estados son neutrales: el verde es de marca, no quiere decir «bien».
- **Todo entra por Django**, que reenvía `/v2/mir/` al servicio del front: el
  mismo login y el mismo middleware que el resto.
- **La API es el único canal**: ver `docs/mir/api.md`.

## Estructura

```text
frontends/
  package.json            workspaces y versiones exactas; un solo lockfile
  Dockerfile              APP=<app>; etapas dev (Vite) y prod (nginx)
  packages/
    ui/                   @mir/ui: tema, layout, etiquetas de estado
    api/                  @mir/api: cliente HTTP, sesión y tipos del esquema OpenAPI
  apps/
    mir/                  la app, bajo /v2/mir/
```

`@mir/ui` y `@mir/api` son **provisorios**: cuando SISOC publique su
`@sisoc/ui` y su `@sisoc/api`, se usan ésos.

## Cómo se trabaja

Con el sistema levantado (`docker compose up -d`), la versión nueva se abre en
**http://localhost:8100/v2/mir/**. Los cambios en `frontends/` se ven solos,
sin recargar.

| Para | Comando |
|---|---|
| Regenerar el contrato de la API | `docker compose exec web python manage.py spectacular --file frontends/packages/api/esquema.yaml` |
| Regenerar los tipos del front desde el contrato | `docker compose exec front_mir npm run tipos` |
| Controlar los tipos | `docker compose exec front_mir npm run chequear` |
| Compilar la versión de producción | `docker compose exec front_mir npm run build` |

**Después de cambiar una respuesta de la API, se regeneran el contrato y los
tipos en el mismo cambio.** Si no, el front compila contra una forma vieja.

## Migrado

| Sección | Estado |
|---|---|
| Inicio | ✅ con su API, en escritorio y en teléfono, modo claro y oscuro |
| Plantillas · Carga · Resultado · Edición · Revisión · Reglas | pendientes |

## Pendientes de la base

Lo que la norma de SISOC incluye y todavía no se sumó, porque la primera
pantalla no lo necesitaba:

- **Pruebas del front** (`vitest` y Testing Library). Al agregarlas, npm chocó
  con una dependencia de Vite; se resuelve cuando se escriban las primeras.
- **ESLint**, **Playwright**, **Sentry** y los formularios
  (`react-hook-form` y `zod`): llegan con la primera pantalla que carga datos.
- **La versión de producción servida en el compose.** Hoy el compose levanta
  Vite en modo desarrollo; la etapa `prod` del Dockerfile está lista, pero
  falta usarla en el despliegue.
