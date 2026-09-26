# Front v2 (React)

**Estado al 25-09-2026:** **todas las pantallas están migradas**, y el circuito
completo se recorrió de punta a punta en el navegador, con cada rol. Rama
`front-react`, sin fusionar a `main`. La versión actual sigue andando igual.

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
**http://localhost:8100/v2/mir/**.

### Dos modos

| Modo | Qué levanta | Cuándo |
|---|---|---|
| **Producción** (por defecto) | La app compilada, servida por nginx. Los archivos con huella se guardan un año en el navegador | Para instalar, probar o mostrar |
| **Desarrollo** | Vite con recarga en caliente: los cambios en `frontends/` se ven solos | Para programar |

El modo lo elige la variable `FRONT_ETAPA` (`prod` o `dev`). Para desarrollar,
se pone `FRONT_ETAPA=dev` en un `.env` en la raíz del repositorio —que no va a
git— y se reconstruye:

```bash
docker compose up -d --build front_mir
```

Los comandos de la tabla que sigue corren en modo desarrollo.

| Para | Comando |
|---|---|
| Correr las pruebas del front | `docker compose exec front_mir npm test` |
| Revisar el código con ESLint | `docker compose exec front_mir npm run lint` |
| Controlar los tipos | `docker compose exec front_mir npm run chequear` |
| Regenerar el contrato de la API | `docker compose exec web python manage.py spectacular --file frontends/packages/api/esquema.yaml` |
| Regenerar los tipos del front desde el contrato | `docker compose exec front_mir npm run tipos` |
| Compilar la versión de producción | `docker compose exec front_mir npm run build` |

**Después de cambiar una respuesta de la API, se regeneran el contrato y los
tipos en el mismo cambio.** Si no, el front compila contra una forma vieja.

### Si hay que regenerar `package-lock.json`

La npm que trae Node 22.14.0 (la 10.9.2) falla al **resolver** este conjunto de
dependencias con un error interno: `Cannot read properties of null (reading
'edgesOut')`. Con npm 11 no pasa, así que se usa npm 11 sólo para generar el
archivo:

```bash
npx -y npm@11.6.2 install
```

**Instalar** a partir del archivo ya generado (`npm ci`, que es lo que hacen la
imagen y cualquier despliegue) funciona con la npm oficial. Verificado el
26-09-2026.

## Migrado

Todas con su API, en escritorio y en teléfono, en modo claro y oscuro.

| Sección | Ruta, bajo `/v2/mir` | Qué se probó en el navegador |
|---|---|---|
| Inicio | `/` | estado del período y de la presentación; herramientas del administrador |
| Plantillas | `/plantillas` | descarga de una y de todas (zip) |
| Carga | `/cargar` | lo que necesita cada archivo; subida por la API |
| Resultado | `/resultado` | cierre de carga, observaciones, circuito |
| Detalle | `/resultado/:id` | problemas del archivo, hallazgos filtrados y paginados, descargas |
| Edición de datos | `/resultado/:id/datos` | corrección con motivo, historial |
| Comprobante | `/presentacion/:id/comprobante` | datos y expediente; se imprime con el aviso de prueba |
| Revisión | `/revision` | observar, habilitar |
| Reglas | `/reglas` | cambiar un rango y deshacerlo, con el período en preparación |

## Pruebas del front

`vitest` con Testing Library, sobre un navegador simulado (jsdom). Prueban lo
que ve y hace la persona:

- que la jurisdicción esté siempre a la vista, y el aviso de datos de prueba;
- que un archivo bloqueado por otro no se pueda subir, y se diga por qué;
- que «Importar» aparezca recién con el archivo elegido, y «Reemplazar» si ya
  estaba;
- que las fechas no se muestren vacías al corregir datos —pasó el 25-09—, que
  un cambio pida confirmación, y que el nivel nacional no pueda editar.

Las pruebas del servidor, que incluyen las de la API, siguen en `runac/tests/`.

## Pendientes de la base

Lo que la norma de SISOC incluye y todavía no se sumó:

- **Playwright**, las pruebas de punta a punta en un navegador real, y
  **Sentry**, el registro de errores.
- **Los formularios con `react-hook-form` y `zod`.** Los de hoy son chicos
  —una observación, un expediente, una respuesta— y no los necesitan; van a
  hacer falta con las pantallas de administración que salgan del diseño de
  roles y circuito.
- **Un control automático en GitHub** que corra las pruebas y el control de
  tipos en cada subida, como el que pide SISOC.
